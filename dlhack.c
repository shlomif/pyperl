#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <dlfcn.h>
#include "pycompat.h"

/* This is a fake perl module that will look for the real thing ('perl2.so')
 * in sys.path and then load this one with the RTLD_GLOBAL set in order to
 * make the symbols available for extension modules that perl might load.
 */

PyMODINIT_FUNC
PyInit_perl(void)
{
    void* handle = NULL;
    const char *err = NULL;
    const char *s;
    Py_ssize_t slen;
    int i, npath;
    size_t len;
    char buf[1024];
    struct stat sb;
    static const char so_name[] = "/perl2" EXT_SUFFIX;

    PyObject *path = PySys_GetObject("path");
    if (path == NULL || !PyList_Check(path)) {
	PyErr_SetString(PyExc_ImportError,
			"sys.path must be a list of directory names");
	return NULL;
    }

    npath = PyList_Size(path);
    for (i = 0; i < npath; i++) {
	PyObject *v = PyList_GetItem(path, i);
	if (!PyUnicode_Check(v))
	    continue;
	s = PyUnicode_AsUTF8AndSize(v, &slen);
	if (s == NULL) {
	    PyErr_Clear();
	    continue;
	}
	len = (size_t)slen;
	if (len + sizeof(so_name) > sizeof(buf))
	    continue; /* Too long */
	strcpy(buf, s);
	if (buf[0] != '/')
	    continue; /* Not absolute */
	if (strlen(buf) != len)
	    continue; /* v contains '\0' */

	strcpy(buf+len, so_name);

	if (stat(buf, &sb))
	    continue;
	if ((handle = dlopen(buf, RTLD_NOW | RTLD_GLOBAL)))
	    break;
	err = dlerror();
    }

    if (handle) {
	PyObject *(*f)(void) = (PyObject *(*)(void))dlsym(handle, "PyInit_perl2");

	if (f)
	    return f();
	else
	    PyErr_SetString(PyExc_ImportError, "PyInit_perl2 entry point not found");
    }
    else
	PyErr_SetString(PyExc_ImportError,
			err ? err : "perl2" EXT_SUFFIX " not found in sys.path");

    return NULL;
}
