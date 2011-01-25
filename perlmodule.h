/* Copyright 2000-2001 ActiveState
 */

/*#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif*/

/* Python < 2.5 compat */
#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
typedef Py_ssize_t (*lenfunc)(PyObject *);
typedef PyObject *(*ssizeargfunc)(PyObject *, Py_ssize_t);
typedef PyObject *(*ssizessizeargfunc)(PyObject *, Py_ssize_t, Py_ssize_t);
typedef int(*ssizeobjargproc)(PyObject *, Py_ssize_t, PyObject *);
typedef int(*ssizessizeobjargproc)(PyObject *, Py_ssize_t, Py_ssize_t, PyObject *);
typedef Py_ssize_t (*readbufferproc)(PyObject *, Py_ssize_t, void **);
typedef Py_ssize_t (*writebufferproc)(PyObject *, Py_ssize_t, void **);
typedef Py_ssize_t (*segcountproc)(PyObject *, Py_ssize_t *);
typedef Py_ssize_t (*charbufferproc)(PyObject *, Py_ssize_t, char **);
#endif

void propagate_errsv(void);
PyObject *call_perl(char *method, SV* obj, I32 gimme,
		    PyObject *args, PyObject *keywds);


#ifdef USE_ITHREADS
 #ifdef MULTI_PERL
   #define SET_CUR_PERL /* empty */
   extern PerlInterpreter* new_perl(void);
   extern void free_perl(PerlInterpreter*);
 #else /* MULTI_PERL */
   extern PerlInterpreter *main_perl;
   #define SET_CUR_PERL do { \
          if (my_perl != main_perl) { \
             my_perl = main_perl; \
             PERL_SET_CONTEXT(my_perl); \
          } \
       } while (0)
   /* we should probably also restore old my_perl if it was not neither
    * NULL nor main_perl, but that can wait.
    */
 #endif /* MULTI_PERL */
#else /* USE_ITHREADS */
   #define SET_CUR_PERL /* empty */
#endif /* USE_ITHREADS */
