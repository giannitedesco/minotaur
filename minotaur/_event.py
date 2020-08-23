from typing import NamedTuple
from pathlib import Path

from ._mask import Mask

__all__ = ('Event',)


class Event(NamedTuple):
    wd: int
    mask: Mask
    cookie: int
    name: Path
