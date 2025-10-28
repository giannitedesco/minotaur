"""
Minotaur. A pythonic, asynchronous, inotify interface.
"""

from ._mask import Mask
from ._base import Inotify, InotifyBase
from ._event import Event
from ._minotaur import Minotaur
from . import _inotify

init = _inotify.init
add_watch = _inotify.add_watch
rm_watch = _inotify.rm_watch

__all__ = (
    'Mask',
    'Inotify',
    'InotifyBase',
    'Minotaur',
    'Event',

    'init',
    'add_watch',
    'rm_watch',
)
