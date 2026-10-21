/* Copyright 2000-2001 ActiveState
 *
 * This file contains various conversion function to map
 * between perl and python datatypes.
 */

#include <EXTERN.h>
#include <perl.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "pycompat.h"
#include "lang_map.h"
#include "lang_lock.h"
#include "thrd_ctx.h"
#include "svrv_object.h"
#include "pyo.h"

/* when the pyo2sv or sv2py functions are called, both the perl and the python
 * lock need to be held.  These functions must guaranty that they will not
 * trigger execution of any perl or python code (like stringify overload or
 * attribute access), but only execute pure api calls.
 */

SV*
pyo2sv(PyObject *o)
{
    dCTXP;

    ASSERT_LOCK_BOTH;

    if (o == Py_None) {
	return newSV(0);
    }
    else if (PyUnicode_Check(o)) {
	Py_ssize_t len;
	const char *s = PyUnicode_AsUTF8AndSize(o, &len);
	if (s == NULL) {
	    /* lone surrogates */
	    PyErr_Clear();
	    return newPerlPyObject_inc(o);
	}
	return newSVpvn_flags(s, len, PyUnicode_IS_ASCII(o) ? 0 : SVf_UTF8);
    }
    else if (PyBytes_Check(o)) {
	return newSVpvn(PyBytes_AS_STRING(o), PyBytes_GET_SIZE(o));
    }
    else if (PyLong_Check(o)) {
	int overflow;
	long long v = PyLong_AsLongLongAndOverflow(o, &overflow);
	if (!overflow && !(v == -1 && PyErr_Occurred()))
	    return newSViv((IV)v);
	if (overflow > 0) {
	    unsigned long long tmp = PyLong_AsUnsignedLongLong(o);
	    if (!(tmp == (unsigned long long)-1 && PyErr_Occurred()))
		return newSVuv((UV)tmp);
	}
	/* too big for IV/UV */
	PyErr_Clear();
	return newPerlPyObject_inc(o);
    }
    else if (PyFloat_Check(o)) {
	return newSVnv(PyFloat_AsDouble(o));
    }
    else if (PySVRV_Check(o)
#ifdef MULTI_PERL
             && ((PySVRV*)o)->owned_by == ctx->perl
#endif
            )
    {
	return SvREFCNT_inc(PySVRV_RV(o));
    }
    else {
	return newPerlPyObject_inc(o);
    }
}


/* character strings (UTF8 flag) and ASCII become str, other byte strings bytes */
static PyObject*
pv2pyo(SV* sv, const char *s, STRLEN len)
{
    STRLEN i;
    if (SvUTF8(sv))
	return PyUnicode_DecodeUTF8(s, (Py_ssize_t)len, "surrogateescape");
    for (i = 0; i < len; i++)
	if (s[i] & 0x80)
	    return PyBytes_FromStringAndSize(s, (Py_ssize_t)len);
    return PyUnicode_DecodeASCII(s, (Py_ssize_t)len, NULL);
}

PyObject*
sv2pyo(SV* sv)
{
    PyObject* po;
    dCTXP;

    ASSERT_LOCK_BOTH;

    if (SvPOK(sv)) {
	STRLEN len;
	char *s = SvPV(sv, len);
	po = pv2pyo(sv, s, len);
    }
    else if (SvNOK(sv)) {
	po = Py_BuildValue("d", SvNV(sv));
    }
    else if (SvIOK(sv)) {
	/* long is 32 bit on Win64 */
	if (SvIsUV(sv))
	    po = PyLong_FromUnsignedLongLong((unsigned long long)SvUV(sv));
	else
	    po = PyLong_FromLongLong((long long)SvIV(sv));
    }
    else if (SvROK(sv) && sv_derived_from(sv, "Python::Object")) {
        IV ival = SvIV(SvRV(sv));
	if (ival) {
	    po = INT2PTR(PyObject*, ival);
	    Py_INCREF(po);
	}
	else {
	    /* Bad PyObject substitution */
	    po = Py_BuildValue("");
	}
    }
    else if (SvROK(sv)) {
	po = PySVRV_New(sv);
    }
    else if (!SvOK(sv)) {
	po = Py_BuildValue("");
    }
    else {
        /* XXX Let's just stringify all other stuff for now. */
	STRLEN len;
	char *s;

	/* Switch to perl only mode in case there are some stringify
         * overloading taking place here.  Is that actually possible?
         */
	PYTHON_UNLOCK;
	s = SvPV(sv, len);
	PYTHON_LOCK;
	po = pv2pyo(sv, s, len);
    }

    ASSERT_LOCK_BOTH;
    return po; 
}

