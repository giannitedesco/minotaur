from typing import Deque, Optional, Type, Literal, Any
from pathlib import Path
from types import TracebackType
from collections import deque
from io import DEFAULT_BUFFER_SIZE
from struct import Struct
import os as _os

import asyncio

from . import _inotify
from ._mask import Mask
from ._event import Event

__all__ = ('InotifyBase', 'Inotify')


class InotifyBase:
    __slots__ = (
        '_nonblock',
        '_cloexec',
        '_fd',
        '_buf',
        '_waitq',
    )

    _event = Struct('=iIII')
    _event_sz = _event.size

    _nonblock: bool
    _cloexec: bool
    _fd: int
    _buf: bytes
    _waitq: Deque[asyncio.Future[None]]

    def __init__(self,
                 blocking: bool = True,
                 cloexec: bool = True,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 ) -> None:

        self._nonblock = not blocking
        self._cloexec = cloexec
        self._fd = -1

        if self._nonblock:
            self._waitq = deque()

    @property
    def closed(self) -> bool:
        """
        True if the inotify fd is closed
        """
        return self._fd < 0

    def open(self) -> None:
        """
        Create the inotify fd
        """

        assert self._fd < 0
        nb = self._nonblock and _inotify.IN_NONBLOCK
        ce = self._cloexec and _inotify.IN_CLOEXEC
        self._fd = _inotify.init(nb | ce)

    def _check_open(self) -> None:
        if self.closed:
            raise ValueError("I/O operation on closed file.")

    def _register_for_read(self) -> None:
        self._check_open()
        assert self._nonblock
        loop = asyncio.get_running_loop()
        loop.add_reader(self._fd, self._fd_readable)

    def _unregister_for_read(self) -> None:
        self._check_open()
        assert self._nonblock
        loop = asyncio.get_running_loop()
        loop.remove_reader(self._fd)

    def _fd_readable(self) -> None:
        """
        Callback for asyncio when the inotify fd has become readable
        """

        while self._waitq:
            w = self._waitq.popleft()
            if not self._waitq:
                self._unregister_for_read()
            if not w.done():
                w.set_result(None)
                break

    def close(self) -> None:
        """
        Close the inotify fd

        This will wake all asynchronous waiters.
        """

        if self.closed:
            return

        if self._nonblock:
            loop = asyncio.get_running_loop()
            try:
                loop.remove_reader(self._fd)
            except ValueError:
                pass

            while self._waitq:
                w = self._waitq.popleft()
                if not w.done():
                    w.set_result(None)

        try:
            _os.close(self._fd)
        finally:
            self._fd = -1

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> 'InotifyBase':
        self.open()
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> Literal[False]:
        self.close()
        return False

    def add_watch(self, p: Path, mask: Mask) -> int:
        """
        Add a watch to the inotify fd.

        Return the watch descriptor (an integer).
        """

        self._check_open()
        path = _os.fsencode(p)
        return _inotify.add_watch(self._fd, path, mask.value)

    def rm_watch(self, wd: int) -> int:
        """
        Remove a watch from the inotify fd, given a watch descriptor
        """

        self._check_open()
        return _inotify.rm_watch(self._fd, wd)

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read raw bytes from the inotify fd.

        This is probably not the interface that you want. Use the iterator
        protocol instead.
        """

        if size is None or size < 0:
            return self.readall()

        self._check_open()
        return _os.read(self._fd, size)

    def readall(self) -> bytes:
        """
        Read all raw bytes from the inotify fd.

        This only works in non-blocking mode, since in blocking mode the
        returned object would, by definition, be infinite in size.
        """

        self._check_open()

        result = bytearray()
        n = DEFAULT_BUFFER_SIZE

        if not self._nonblock:
            raise ValueError("Can't readall on blocking inotify")

        while True:
            try:
                chunk = _os.read(self._fd, n)
            except BlockingIOError:
                if result:
                    break
                return b''
            if not chunk:
                break
            result += chunk

        return bytes(result)

    def __iter__(self) -> 'InotifyBase':
        self._check_open()

        if self._nonblock:
            raise ValueError("Synchronous iiter used on non-blocking inotify")

        if hasattr(self, '_buf'):
            raise ValueError("Concurrent iteration on inotify fd")

        self._buf = b''
        return self

    def __aiter__(self) -> 'InotifyBase':
        self._check_open()

        if not self._nonblock:
            raise ValueError("Async iiter used on blocking inotify")

        if hasattr(self, '_buf'):
            raise ValueError("Concurrent iteration on inotify fd")

        self._buf = b''
        return self

    def _fill_buffer(self, chunk_size: int = DEFAULT_BUFFER_SIZE) -> bool:
        """
        Read chunk_size bytes from the fd and append to the internal buffer.
        """

        chunk = self.read(chunk_size)
        if self._buf:
            self._buf += chunk
        else:
            self._buf = chunk
        return bool(chunk)

    def _buf_pop(self) -> Optional[Event]:
        """
        Parse the first event frm the buffer and return it as an Event object.
        If there is not enough data in the buffer then return None.
        """

        hdr_len = self._event_sz

        if len(self._buf) < hdr_len:
            return None

        wd, mask, cookie, evlen = self._event.unpack_from(self._buf)

        tot_len = hdr_len + evlen
        if len(self._buf) < tot_len:
            return None

        path_buf = self._buf[hdr_len:tot_len]
        try:
            nul = path_buf.find(0)
        except ValueError:
            pass
        else:
            path_buf = path_buf[:nul]

        path = _os.fsdecode(path_buf)
        self._buf = self._buf[tot_len:]

        return Event(wd, Mask(mask), cookie, Path(path))

    def _next_event(self) -> Optional[Event]:
        while not self.closed:
            ret = self._buf_pop()
            if ret:
                return ret

            self._fill_buffer()

        return None

    async def _next_event_async(self) -> Optional[Event]:
        while not self.closed:
            ret = self._buf_pop()
            if ret:
                return ret

            if not self._fill_buffer(-1):
                loop = asyncio.get_running_loop()

                if not self._waitq:
                    self._register_for_read()
                wake = loop.create_future()
                self._waitq.append(wake)
                await wake

        return None

    def __next__(self) -> Any:
        raise NotImplementedError

    async def __anext__(self) -> Any:
        raise NotImplementedError


class Inotify(InotifyBase):
    def __next__(self) -> Event:
        evt = self._next_event()
        if evt is not None:
            return evt
        raise StopIteration

    async def __anext__(self) -> Event:
        evt = await self._next_event_async()
        if evt is not None:
            return evt
        raise StopIteration
