# Minotaur: A pythonic, asynchronous, inotify interface

<div align="center">
  <img src="https://img.shields.io/pypi/v/minotaur?label=pypi" alt="PyPI version">
</div>


## Examples

Minotaur provides the `Inotify` class which is to be used as a context
manager, from within which, one may iterate over inotify events:

```python
    with Inotify() as n:
        n.add_watch('.', Mask.CREATE | Mask.DELETE | Mask.MOVE)
        for evt in n:
            print(evt)
```

The asynchronous interface works almost identically. The inotify object must
be created in nonblocking mode, and then the mere addition of the `async`
keyword to the iteration over events is all that's required:

```python
    with Inotify(blocking=False) as n:
        n.add_watch('.', Mask.CREATE | Mask.DELETE | Mask.MOVE)
        async for evt in n:
            print(evt)
```

Example output would look like this:

```python
Event(wd=1, mask=<Mask.CREATE: 256>, cookie=0, name=PosixPath('foo'))
Event(wd=1, mask=<Mask.CREATE: 256>, cookie=0, name=PosixPath('bar'))
Event(wd=1, mask=<Mask.MOVED_FROM: 64>, cookie=129399, name=PosixPath('foo'))
Event(wd=1, mask=<Mask.MOVED_TO: 128>, cookie=129399, name=PosixPath('baz'))
Event(wd=1, mask=<Mask.DELETE: 512>, cookie=0, name=PosixPath('bar'))
Event(wd=1, mask=<Mask.DELETE: 512>, cookie=0, name=PosixPath('baz'))

```

There is also a command-line tool demonstrating the features
```bash
$ python -m minotaur --help

usage: minotaur [-h] [--async | --sync] [--fancy] [--mask MASK] dir [dir ...]

Minotaur: A pythonic, asynchronous, inotify interface.

A summary of inotify watch flags:
 - ACCESS: File was accessed
 - ATTRIB: Metaata changed, eg. permissions
 - CLOSE_WRITE: File for writing was closed
 - CLOSE_NOWRITE: File or dir not opened for writing was closed
 - CREATE: File/dir was created
 - DELETE: File or dir was deleted
 - DELETE_SELF: Watched file/dir was itself deleted
 - MODIFY: File was modified
 - MOVE_SELF: Watched file/dir was itself moved
 - MOVED_FROM: Generated for dir containing old filename when a file is renamed
 - MOVED_TO: Generated for dir containing new filename when a file is renamed
 - OPEN: File or dir was opened
 - MOVE: MOVED_FROM | MOVED_TO
 - CLOSE: IN_CLOSE_WRITE | IN_CLOSE_NOWRITE
 - DONT_FOLLOW: Don't dereference pathname if it is a symbolic link
 - EXCL_UNLINK: Don't generate events after files have been unlinked
 - ONESHOT: Only generate one event for this watch
 - ONLYDIR: Watch pathname only if it is a dir
 - MASK_CREATE: Only watch path if it isn't already being watched

positional arguments:
  dir                   Watch for events in given dir

optional arguments:
  -h, --help            show this help message and exit
  --async, -a           Use asyncio event loop
  --sync, -s            Use synchronous interface
  --fancy, -f           Use fancy interface
  --mask MASK, -m MASK  Events to watch for

```

## What is different about Minotaur?

1. C interface provides basic wrapper to syscalls and constants. In future, if
   performance becomes a problem, more functionality can be gradually moved
   there.

2. Pythonic. `IntFlags` is used for watch types. Context-managers take care of
   fd lifetime, `close()` method is idempotent. Raw `read()` and `readall()`
   methods work comparably to python standard `io` objects. Full support for
   `mypy`, including typeshed for C interface. Iterator and async-iterator
   protocols supported.

3. Makes no assumptions about the name encoding of filesystems, ie. with
   `os.fsencode()` and `os.fsdecode()`

4. Async interface supports multiple concurrent waiters. Waiting tasks are
   woken in a first-come, first-serve manner.

5. Users can choose between different levels of support:
   1. Raw syscall interface
   2. Low-level inotify object, which takes care of path encoding, reading of
	raw inotify data, parsing of binary events in to python objects, and
	provides both synchronous and async interface. But is still low-level
	because it does no special handling of watches or combining of related
	events (eg.`MOVE_FROM` / `MOVE_TO`).
   3. Fancy high-level interfaces, in pure python, built on top of low-level
        interface.

## What is missing

There is no attempt to abstract file-notification functionality offered by
other operating systems in to a cross-platform interface.

There are no tests.

## Development
You should use the provided pre-commit hooks to make sure code type-checks and
is PEP-8 formatted:

```bash
ln -sf ../../pre-commit.sh .git/hooks/pre-commit
```

## Why another one?

There are several other python inotify packages. So why does this one exist?
Well, this can perhaps be explained best by referring to some of the others:

1. `PyInotify`: suffers from numerous bugs. The fd closes aren't idempotent,
   this can lead to closing unrelated file descriptors. This would be less of
   an issue if the fd had a clear ownership and lifetime, or used context
   managers. In other words, it's difficult to use safely.

2. `PyInotify`: Assumes utf-8 filesystem encoding. No `asyncio` interface.

3. `inotify_simple`: Nicely subclasses `FileIO`, but that precludes `asyncio`
   since `FileIO` is meant for blocking I/O on files and cannot be easily
   adapted for other purposes.

4. `python_inotify`: No `asyncio` interface and, it would need to be added in
   the C code, or if added in python code would duplicate the C code and work
   differently, thus being a new API.

5. `python-inotify`: It's packaged by RedHat but, similarly to
   `python_inotify` the read() syscall is done in the C extension so it
   doesn't support `asyncio`, and can't easily be adapted to do so without
   changing the interface or duplicating functionality.

6. `asyncinotify`: Easily the best of the bunch. The main downside is that it
   doesn't provide a synchronous interface or low-level interfaces.

The others seem to be parts of larger projects, or systems.
