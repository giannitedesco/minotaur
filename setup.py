#!/usr/bin/env python3

from typing import Dict, Any
from pathlib import Path
import setuptools

_c_extension = setuptools.Extension('minotaur._inotify',
                                    ['minotaur/_inotify.c', ])

version_file = Path('minotaur/__version__.py')
v: Dict[str, Any] = {}
exec(version_file.read_text(), v)

setuptools.setup(
    name=v['__title__'],
    version=v['__version__'],
    description=v['__description__'],
    author=v['__author__'],
    author_email=v['__author_email__'],
    package_data={
        'minotaur': ['py.typed'],
    },
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    license=v['__license__'],
    platforms='Linux',
    packages=[
        'minotaur',
    ],
    url=v['__url__'],
    ext_modules=[_c_extension, ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
