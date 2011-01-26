#!/usr/bin/env python

import sys
import os
import re
import unittest
import perl

expect_re = re.compile(r"^1\.\.(\d+)$")
ok_re     = re.compile(r"^(not\s+)?ok\s+(\d+)$")

class TestPyPerlBasic(unittest.TestCase):

    def setUp(self):

        perl.eval("""
sub foo2 {
    wantarray ? (1, 2, 3) : 42;
}
""")

    def test_simple_calculator(self):
        # try to use perl as a simple calculator
        self.assertEquals(perl.eval("3+3"), 6)

    def test_pass_strings_back(self):
        # can we pass strings back
        assertEquals(perl.eval("substr('abcd', 0, 3)"), "abc")

    def test_pass_hashes_both_ways(self):
        # can we pass hashes both ways
        if perl.MULTI_PERL:
            skip("not on MULTI_PERL...")
        else:
            perl.eval("sub foo_elem { shift->{foo} }")
            hash = perl.eval("{ foo => 42 }")
            self.assertEqual(perl.call("foo_elem", hash), 42)

    def test_trap_exceptions(self):
        # try to trap exceptions
        try:
            perl.eval("die 'Oops!'")
        except perl.PerlError, val:
	    assertEqual(str(val)[:5],"Oops!")

        try:
            perl.call("not_there", 3, 4)
        except perl.PerlError, val:
            assertEqual(str(val), "Undefined subroutine &main::not_there called.\n")


    def test_function_scalar_context(self):
        # scalar context
        assertEqual(perl.call("foo2"), 42)

    def test_function_array_context_tuple_back(self):
        res = perl.call_tuple("foo2")
        assertEqual(len(res), 3)
        assertEqual(res[0], 1)
        assertEqual(res[1], 2)
        assertEqual(res[2], 3)

    def test_anonymous_perl_functions(self):
        # can we call anonymous perl functions
        # can we pass hashes both ways
        if perl.MULTI_PERL:
            self.skip("not on MULTI_PERL...")
        else:
            func = perl.eval("sub { $_[0] + $_[1] }")
            self.assertEquals(int(func(3, 4)), 7)

class TestPyPerlDefined(unittest.TestCase):

    def setUp(self):
	perl.eval("""

sub foo;

sub bar { }

@baz = ();

$Foo::bar = 33;

""")
    def test_defined(self)
	self.assertFalse(perl.defined("baz"))

	self.assertTrue(not perl.defined("foo") and perl.defined("bar"))

	self.assertTrue(perl.defined("@baz"))

	self.assertTrue(perl.defined("$Foo::bar"))

	self.assertTrue(perl.defined(" $Foo::bar"))

def test_main():
    from test import test_support
    test_support.run_unittest(TestPyPerlBasic)
    test_support.run_unittest(TestPyPerlDefined)

if __name__ == "__main__":
    test_main()
