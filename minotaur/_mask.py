from typing import Optional
from enum import IntFlag as _IntFlag

from . import _inotify


__all__ = ('Mask',)


class Mask(_IntFlag):
    show_help: bool

    def __new__(cls,
                value: int,
                doc: Optional[str] = None,
                show_help: bool = True) -> 'Mask':
        self = int.__new__(cls, value)
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
            self.show_help = show_help
        return self

    """
    Flags for establishing inotify watches.
    """

    ACCESS = _inotify.IN_ACCESS, 'File was accessed'
    ATTRIB = _inotify.IN_ATTRIB, 'Metaata changed, eg. permissions'
    CLOSE_WRITE = _inotify.IN_CLOSE_WRITE, 'File for writing was closed'
    CLOSE_NOWRITE = _inotify.IN_CLOSE_NOWRITE, \
        'File or dir not opened for writing was closed'
    CREATE = _inotify.IN_CREATE, 'File/dir was created'
    DELETE = _inotify.IN_DELETE, 'File or dir was deleted'
    DELETE_SELF = _inotify.IN_DELETE_SELF, \
        'Watched file/dir was itself deleted'
    MODIFY = _inotify.IN_MODIFY, 'File was modified'
    MOVE_SELF = _inotify.IN_MOVE_SELF, 'Watched file/dir was itself moved'
    MOVED_FROM = _inotify.IN_MOVED_FROM, \
        'Generated for dir containing old filename when a file is renamed'
    MOVED_TO = _inotify.IN_MOVED_TO, \
        'Generated for dir containing new filename when a file is renamed'
    OPEN = _inotify.IN_OPEN, 'File or dir was opened'
    MOVE = _inotify.IN_MOVE, 'MOVED_FROM | MOVED_TO'
    CLOSE = _inotify.IN_CLOSE, 'IN_CLOSE_WRITE | IN_CLOSE_NOWRITE'

    DONT_FOLLOW = _inotify.IN_DONT_FOLLOW, \
        "Don't dereference pathname if it is a symbolic link"
    EXCL_UNLINK = _inotify.IN_EXCL_UNLINK, \
        "Don't generate events after files have been unlinked"

    MASK_ADD = _inotify.IN_MASK_ADD, 'Add flags to an existing watch', False

    ONESHOT = _inotify.IN_ONESHOT, 'Only generate one event for this watch'
    ONLYDIR = _inotify.IN_ONLYDIR, 'Watch pathname only if it is a dir'
    MASK_CREATE = _inotify.IN_MASK_CREATE, \
        "Only watch path if it isn't already being watched"

    # These are returned in events
    IGNORED = _inotify.IN_IGNORED, 'Watch was removed', False
    ISDIR = _inotify.IN_ISDIR, 'This event is a dir', False
    Q_OVERFLOW = _inotify.IN_Q_OVERFLOW, 'Event queue overflowed', False
    UNMOUNT = _inotify.IN_UNMOUNT, \
        'Filesystem containing watched object was unmounted', False

    EVENT_TYPE = _inotify.EVENT_TYPE_MASK, 'Mask of all event types', False
