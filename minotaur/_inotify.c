#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <sys/inotify.h>

#ifndef IN_MASK_CREATE
#define IN_MASK_CREATE 0x10000000 /* new in Linux 4.19 */
#endif

static PyObject *_inotify_init(PyObject *self, PyObject *args)
{
	int flags = 0, ret;

	if (!PyArg_ParseTuple(args, "|i", &flags))
		return NULL;

	ret = inotify_init1(flags);
	if (ret < 0) {
		return PyErr_SetFromErrno(PyExc_OSError);
	}

	return PyLong_FromLong(ret);
}

static PyObject *_inotify_add_watch(PyObject *self, PyObject *args)
{
	int fd, ret;
	unsigned int mask;
	char *path;

	if (!PyArg_ParseTuple(args, "iyI", &fd, &path, &mask))
		return NULL;

	ret = inotify_add_watch(fd, path, mask);
	if (ret < 0) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}

	return PyLong_FromLong(ret);
}

static PyObject *_inotify_rm_watch(PyObject *self, PyObject *args)
{
	int fd, wd, ret;

	if (!PyArg_ParseTuple(args, "ii", &fd, &wd))
		return NULL;

	ret = inotify_rm_watch(fd, wd);
	if (ret < 0) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}

	return PyLong_FromLong(ret);
}

static PyMethodDef _inotify_methods[] = {
	{
		"init",
		_inotify_init,
		METH_VARARGS,
		"Create inotify fd."
	},
	{
		"add_watch",
		_inotify_add_watch,
		METH_VARARGS,
		"Add watch to inotify fd."
	},
	{
		"rm_watch",
		_inotify_rm_watch,
		METH_VARARGS,
		"Remove watch from inotify fd."
	},
	{
		NULL,
	},
};

static struct PyModuleDef _inotify_module = {
	PyModuleDef_HEAD_INIT,
	"_inotify",
	NULL,
	-1,
	_inotify_methods,
};

PyMODINIT_FUNC
PyInit__inotify(void)
{
	PyObject *m;

	m = PyModule_Create(&_inotify_module);
	if (m == NULL)
		return NULL;

	PyModule_AddIntMacro(m, IN_NONBLOCK);
	PyModule_AddIntMacro(m, IN_CLOEXEC);

	PyModule_AddIntMacro(m, IN_ACCESS);
	PyModule_AddIntMacro(m, IN_ATTRIB);
	PyModule_AddIntMacro(m, IN_CLOSE_WRITE);
	PyModule_AddIntMacro(m, IN_CLOSE_NOWRITE);
	PyModule_AddIntMacro(m, IN_CREATE);
	PyModule_AddIntMacro(m, IN_DELETE);
	PyModule_AddIntMacro(m, IN_DELETE_SELF);
	PyModule_AddIntMacro(m, IN_MODIFY);
	PyModule_AddIntMacro(m, IN_MOVE_SELF);
	PyModule_AddIntMacro(m, IN_MOVED_FROM);
	PyModule_AddIntMacro(m, IN_MOVED_TO);
	PyModule_AddIntMacro(m, IN_OPEN);

	PyModule_AddIntMacro(m, IN_MOVE);
	PyModule_AddIntMacro(m, IN_CLOSE);

	PyModule_AddIntMacro(m, IN_DONT_FOLLOW);
	PyModule_AddIntMacro(m, IN_EXCL_UNLINK);
	PyModule_AddIntMacro(m, IN_MASK_ADD);
	PyModule_AddIntMacro(m, IN_ONESHOT);
	PyModule_AddIntMacro(m, IN_ONLYDIR);
	PyModule_AddIntMacro(m, IN_MASK_CREATE);

	PyModule_AddIntMacro(m, IN_IGNORED);
	PyModule_AddIntMacro(m, IN_ISDIR);
	PyModule_AddIntMacro(m, IN_Q_OVERFLOW);
	PyModule_AddIntMacro(m, IN_UNMOUNT);

#define EVENT_TYPE_MASK (0xfff)
	PyModule_AddIntMacro(m, EVENT_TYPE_MASK);

	return m;
}
