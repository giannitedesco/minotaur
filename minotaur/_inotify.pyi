def init(flags: int = 0) -> int: ...
def add_watch(fd: int, path: bytes, flags: int) -> int: ...
def rm_watch(fd: int, wd: int) -> int: ...

IN_NONBLOCK: int
IN_CLOEXEC: int

IN_ACCESS: int
IN_ATTRIB: int
IN_CLOSE_WRITE: int
IN_CLOSE_NOWRITE: int
IN_CREATE: int
IN_DELETE: int
IN_DELETE_SELF: int
IN_MODIFY: int
IN_MOVE_SELF: int
IN_MOVED_FROM: int
IN_MOVED_TO: int
IN_OPEN: int

IN_MOVE: int
IN_CLOSE: int

IN_DONT_FOLLOW: int
IN_EXCL_UNLINK: int
IN_MASK_ADD: int
IN_ONESHOT: int
IN_ONLYDIR: int
IN_MASK_CREATE: int

IN_IGNORED: int
IN_ISDIR: int
IN_Q_OVERFLOW: int
IN_UNMOUNT: int

EVENT_TYPE_MASK: int
