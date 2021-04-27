#!/usr/bin/perl

use strict;
use warnings;

my %func;
my $prop;

open(my $H, ">", "try_perlapi.h") || die;
open(my $C, ">", "try_perlapi.c") || die;

my $note = "/* DO NOT EDIT!!!\n * Autogenerated by $0\n */\n\n";
print {$H} $note;
print {$C} $note;

my $ENABLE_JMPENV = $^O ne "MSWin32";

print {$C} <<"EOT";

#include <EXTERN.h>
#define PERL_EXT 1
#include <perl.h>
#include <Python.h>

#include "try_perlapi.h"
#include "perlmodule.h"
#include "lang_lock.h"
#include "thrd_ctx.h"
EOT

print {$C} <<"EOT" if $ENABLE_JMPENV;

static LOGOP dummy_op;

void
fake_inittry(void)
{
    Zero(&dummy_op, 1, LOGOP);
    dummy_op.op_flags |= OPf_WANT_SCALAR;
    dummy_op.op_next = Nullop;
}

static void
fake_entertry(PERL_CONTEXT **cx_ptr)
{
    PERL_CONTEXT *cx;
    I32 gimme;
    dCTXP;

    PL_op = (OP*)&dummy_op;
    gimme = GIMME_V;

    ENTER;
    SAVETMPS;
    dMARK;

//    Perl_push_return(aTHX_ Nullop);
    *cx_ptr = cx = cx_pushblock((CXt_EVAL|CXp_TRYBLOCK), gimme, MARK, PL_stack_sp);
    #define WITHOUT_PUSHEVAL
    #ifndef WITHOUT_PUSHEVAL
    PUSHEVAL(cx, 0);
        #endif
    PL_eval_root = PL_op;
    PL_in_eval = EVAL_INEVAL;
    sv_setpvn(ERRSV, "", 0);
}

static void
fake_leavetry(I32 oldscope, PERL_CONTEXT *cx)
{
    dCTXP;
    if (PL_scopestack_ix > oldscope) {
        PMOP *newpm;
        I32 optype;
        SV **newsp;
        I32 gimme;

        CX_LEAVE_SCOPE(cx);
        #if 0
        cx_popsub(cx);
                #endif
        cx_popblock(cx);
    #ifndef WITHOUT_PUSHEVAL
        POPEVAL(cx);
        #endif
        #if 0
        CX_POP(cx);
        #endif
//        Perl_pop_return(aTHX);
        PL_curpm = newpm;
    }

    FREETMPS;
    LEAVE;
}

EOT

print {$H} "void \tfake_inittry(void);\n";

while (<DATA>) {
    if (/^(\w.*?)(\w+)\(([^)]*)\)\s*$/) {
	gen_func() if %func;
	%func = ();
	undef($prop);
	@func{qw/type name args/} = ($1, $2, $3);

	# some trimming
	for (@func{qw/type args/}) {
	    s/^\s+//;
	    s/\s+$//;
	}
    }
    elsif (s/\s+(\w+)\s*:\s*//) {
	$prop = lc($1);
	$func{$prop} = $_;
	if ($prop eq "code" && !/^\s*$/) {
	    chomp($func{code});
	    $func{code} = "RETVAL = $func{code};";
	}
    }
    elsif ($prop) {
	$func{$prop} .= $_;
    }
    elsif (%func) {
	warn;
    }
    else {
	print;
    }
}
gen_func() if %func;
exit;
#-----------

sub gen_func
{
    print {$H} "$func{type}\ttry_$func{name}($func{args});\n";

    my $fail = $func{fail};
    $fail = -1 unless defined $fail;
    $fail =~ s/\s+$//;

    my $code = $func{code} || die;
    $code =~ s/\s+$//s;

    # fix code indentation
    my $indent = 9999;
    my @code = split(/^/, $code);
    for (@code) {
	1 while s/\t/' ' x (8 - length($`) % 8)/e;  # expand tabs

	/^(\s*)/ || die;
	my $i = length($1);
	$indent = $i if $i < $indent;
    }

    if ($indent < 8) {
	for (@code) {
	    $_ = (" " x (8 - $indent)) . $_;
	}
    }
    $code = join("", @code);

    if ($ENABLE_JMPENV) {
	print {$C} <<"EOT";
$func{type}
try_$func{name}($func{args})
{
    dJMPENV;
    dCTXP;
    PERL_CONTEXT *cx=NULL;
    int jmp_status;
    volatile I32 oldscope = PL_scopestack_ix;
    $func{type} RETVAL;

    ASSERT_LOCK_PERL;
    fake_entertry(&cx);

    JMPENV_PUSH(jmp_status);
    if (jmp_status == 0) {

$code

    }
    else if (jmp_status == 3) {
        /* caught an exception, \$@ should be set */
        assert(SvTRUE(ERRSV));
        PYTHON_LOCK;
        propagate_errsv();
        PYTHON_UNLOCK;

        RETVAL = $fail;
    }
    else {
        fprintf(stderr, "should not happen, jmp_status = %d\\n", jmp_status);
    }
    JMPENV_POP;
    fake_leavetry(oldscope, cx);
    return RETVAL;
}

EOT

    }
    else {
	print {$C} <<"EOT";
$func{type}
try_$func{name}($func{args})
{
    dCTXP;
    $func{type} RETVAL;
$code
    return RETVAL;
}

EOT
    }
}

########################################################################

__DATA__

int array_len(AV* av)
   FAIL: -1
   CODE: av_len(av)+1

SV** av_fetch(AV* av, I32 key, I32 lval)
   FAIL: NULL
   CODE: av_fetch(av, key, lval)

int SvGETMAGIC(SV* sv)
   FAIL: -1
   CODE:
     SvGETMAGIC(sv);
     RETVAL = 0;

int SvSETMAGIC(SV* sv)
   FAIL: -1
   CODE:
     SvSETMAGIC(sv);
     RETVAL = 0;
