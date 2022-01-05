from typing import Sequence, Type
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from functools import reduce
from operator import or_
import asyncio
import re

from minotaur import Inotify, Mask, Minotaur, InotifyBase
from minotaur import __title__


_splitter = re.compile(r'[,\.|:\-\s]+')


def _sync_main(cls: Type[InotifyBase],
               dirs: Sequence[Path],
               mask: Mask,
               ) -> None:
    with cls() as n:
        for p in dirs:
            wd = n.add_watch(p, mask)
            print(f'{p.resolve()}: wd={wd}')

        for evt in n:
            print(evt)


async def _task(cls: Type[InotifyBase],
                dirs: Sequence[Path],
                mask: Mask,
                ) -> None:
    with cls(blocking=False) as n:
        for p in dirs:
            wd = n.add_watch(p, mask)
            print(f'{p.resolve()}: wd={wd}')

        async for evt in n:
            print(evt)


def _async_main(cls: Type[InotifyBase],
                dirs: Sequence[Path],
                mask: Mask,
                ) -> None:
    asyncio.run(_task(cls, dirs, mask))


_mask_help = '\n'.join((f' - {x.name}: {x.__doc__}'
                        for x in Mask if x.show_help))

_prog_desc = f"""
Minotaur: A pythonic, asynchronous, inotify interface.

A summary of inotify watch flags:
{_mask_help}
"""

_default_mask = 'create,delete,delete_self,moved_from,moved_to'


def _main() -> None:
    opts = ArgumentParser(prog=__title__,
                          formatter_class=RawTextHelpFormatter,
                          description=_prog_desc)

    opts.set_defaults(func=_async_main, cls=Inotify)

    g = opts.add_mutually_exclusive_group(required=False)
    g.add_argument('--async', '-a',
                   dest='func',
                   action='store_const',
                   const=_async_main,
                   help='Use asyncio event loop')
    g.add_argument('--sync', '-s',
                   dest='func',
                   action='store_const',
                   const=_sync_main,
                   help='Use synchronous interface')

    opts.add_argument('--fancy', '-f',
                      dest='cls',
                      action='store_const',
                      const=Minotaur,
                      help='Use fancy interface')
    opts.add_argument('--mask', '-m',
                      default=_default_mask,
                      help='Events to watch for')
    opts.add_argument('dir',
                      nargs='+',
                      type=Path,
                      help='Watch for events in given dir')

    args = opts.parse_args()

    flags = (Mask[tok.upper()] for tok in _splitter.split(args.mask))
    mask = reduce(or_, flags)

    args.func(args.cls, args.dir, mask)


if __name__ == '__main__':
    _main()
