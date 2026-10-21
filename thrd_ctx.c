/*
 * Thread context (only used for MULTI_PERL builds)
 *
 * Copyright 2000-2001 ActiveState
 *
 */

#include <EXTERN.h>
#include <perl.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "pycompat.h"
#include "thrd_ctx.h"
#include "perlmodule.h"

static perl_key thrd_ctx_key;

#ifdef WIN32
void free_thread_ctx(thread_ctx* ctx);
static int finalizing = 0;

static void
python_finalized(void)
{
    finalizing = 1;
}

/* runs at thread exit, outside the loader lock (unlike DllMain) */
static VOID WINAPI
fls_free_thread_ctx(PVOID ctx)
{
    if (ctx && !finalizing)
	free_thread_ctx((thread_ctx*)ctx);
}
#endif

thread_ctx*
get_thread_ctx(void)
{
    thread_ctx* ctx;
#ifdef WIN32
    ctx = (thread_ctx*)FlsGetValue(thrd_ctx_key);
#else
    ctx = (thread_ctx*)pthread_getspecific(thrd_ctx_key);
#endif
    if (!ctx) {
	refcounted_perl* p = (refcounted_perl*)PyMem_RawMalloc(sizeof(refcounted_perl));
	ctx = (thread_ctx*)PyMem_RawMalloc(sizeof(thread_ctx));
	if (!p || !ctx) {
	    Py_FatalError("Can't allocate memory for thread context");
	}
	/* fprintf(stderr, "Allocated new thread context %p\n", ctx); */
	memset(ctx, 0, sizeof(thread_ctx));

	p->my_perl = new_perl();
	p->refcnt = 0;
	p->thread_done = 0;
	PERL_SET_CONTEXT(p->my_perl);

	ctx->perl = p;
#ifdef WIN32
	FlsSetValue(thrd_ctx_key, (void*)ctx);
#else
	pthread_setspecific(thrd_ctx_key, (void*)ctx);
#endif
    }
    return ctx;
}

void
free_thread_ctx(thread_ctx* ctx)
{
    /* fprintf(stderr, "thread ctx free %p\n", ctx); */
    if (ctx->perl->refcnt == 0) {
	free_perl(ctx->perl->my_perl);
	ctx->perl->my_perl = 0;
	PyMem_RawFree(ctx->perl);
    }
    else {
	/* fprintf(stderr, "still %d references left\n", ctx->perl->refcnt); */
	ctx->perl->thread_done = TRUE;
    }
    ctx->perl = 0;
    PyMem_RawFree(ctx);
}

void
thrd_ctx_init()
{
#ifdef WIN32
    Py_AtExit(python_finalized);
    if ((thrd_ctx_key = FlsAlloc(fls_free_thread_ctx)) == FLS_OUT_OF_INDEXES)
#else
    if (pthread_key_create(&thrd_ctx_key, (void*)free_thread_ctx))
#endif
    {
	Py_FatalError("Can't create TSD key for thrd_ctx");
    }

#ifdef BOOT_FROM_PERL
    {
	dTHX;
	refcounted_perl* p = (refcounted_perl*)PyMem_RawMalloc(sizeof(refcounted_perl));
	thread_ctx* ctx = (thread_ctx*)PyMem_RawMalloc(sizeof(thread_ctx));
	if (!p || !ctx) {
	    Py_FatalError("Can't allocate memory for thread context");
	}
	/* fprintf(stderr, "Allocated new thread context %p\n", ctx); */
	memset(ctx, 0, sizeof(thread_ctx));

	p->my_perl = my_perl;
	p->refcnt = 0;
	p->thread_done = 0;

	ctx->perl = p;
#ifdef WIN32
	FlsSetValue(thrd_ctx_key, (void*)ctx);
#else
	pthread_setspecific(thrd_ctx_key, (void*)ctx);
#endif
    }
#endif

}
