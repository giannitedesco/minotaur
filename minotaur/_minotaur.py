from typing import Dict, Tuple, Optional
from pathlib import Path

import asyncio

from ._mask import Mask
from ._event import Event
from ._base import InotifyBase

__all__ = ('Minotaur',)


class Notification:
    __slots__ = (
        '_path',
        '_type',
        '_isdir',
        '_unmount',
        '_qoverflow',
    )

    def __init__(self,
                 path: Path,
                 type: Mask,
                 isdir: bool,
                 unmount: bool,
                 qoverflow: bool = False):
        self._path = path
        self._type = type
        self._isdir = bool(isdir)
        self._unmount = bool(unmount)
        self._qoverflow = bool(qoverflow)

    @property
    def isdir(self) -> bool:
        return self._isdir

    @property
    def unmount(self) -> bool:
        return self._unmount

    @property
    def qoverflow(self) -> bool:
        return self._qoverflow

    @property
    def path(self) -> Path:
        return self._path

    def __repr__(self) -> str:
        t = self._isdir and 'dir' or 'file'
        return f'{type(self).__name__}({self._type.name} {t} {self._path})'

    @classmethod
    def create(cls, path: Path, mask: Mask) -> 'Notification':
        return cls(path,
                   mask & Mask.EVENT_TYPE,
                   bool(mask & Mask.ISDIR),
                   bool(mask & Mask.UNMOUNT),
                   bool(mask & Mask.Q_OVERFLOW))


class Minotaur(InotifyBase):
    """
    Fancy interface for Inotify which does questionable things like:

    1. Resolve watch-descriptors back to paths (which races with renames of
       original paths and can't be used safely, but other inotify packages
       provide this feature, so here it is for your delectation).
    2. Link rename_from/rename_to events together. This feature would be
       useful but isn't yet actually implemented. Working on it...
    """

    __slots__ = (
        '_wdmap',
        '_cmap',
    )

    _wdmap: Dict[int, Path]
    _cmap: Dict[Tuple[int, int], Event]

    def __init__(self,
                 blocking: bool = True,
                 cloexec: bool = True,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 ) -> None:
        super().__init__(blocking, cloexec, loop)
        self._wdmap = {}
        self._cmap = {}

    def add_watch(self, p: Path, mask: Mask) -> int:
        try:
            wd = super().add_watch(p, mask)
        except Exception:
            raise
        else:
            self._wdmap[wd] = p.resolve()
        return wd

    def rm_watch(self, wd: int) -> int:
        try:
            return super().rm_watch(wd)
        except Exception:
            raise
        else:
            del self._wdmap[wd]

    def _resolve_path(self, wd: int, name: Path) -> Path:
        try:
            base_dir = self._wdmap[wd]
        except KeyError:
            path = name
        else:
            path = base_dir / name

        return path

    def __next__(self) -> Notification:
        evt = super()._next_event()
        if evt is None:
            raise StopIteration

        # TODO: Link rename_from/rename_to together if we have them
        path = self._resolve_path(evt.wd, evt.name)
        return Notification.create(path, evt.mask)

    async def __anext__(self) -> Notification:
        evt = await super()._next_event_async()
        if evt is None:
            raise StopIteration

        path = self._resolve_path(evt.wd, evt.name)
        return Notification.create(path, evt.mask)
