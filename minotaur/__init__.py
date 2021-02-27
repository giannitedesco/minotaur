"""
Minotaur. A pythonic, asynchronous, inotify interface.
"""

from .__version__ import \
    __title__, \
    __description__, \
    __url__, \
    __author__, \
    __author_email__, \
    __copyright__, \
    __license__, \
    __version__

from ._mask import Mask
from ._base import Inotify, InotifyBase
from ._event import Event
from ._minotaur import Minotaur
from . import _inotify

init = _inotify.init
add_watch = _inotify.add_watch
rm_watch = _inotify.rm_watch

__all__ = (
    '__title__',
    '__description__',
    '__url__',
    '__author__',
    '__author_email__',
    '__copyright__',
    '__license__',
    '__version__',

    'Mask',
    'Inotify',
    'InotifyBase',
    'Minotaur',
    'Event',

    'init',
    'add_watch',
    'rm_watch',
)
