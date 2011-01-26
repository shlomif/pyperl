#!/usr/bin/env python

import unittest
import perl

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
        self.assertEquals(perl.eval("substr('abcd', 0, 3)"), "abc")

    def test_pass_hashes_both_ways(self):
        # can we pass hashes both ways
        if perl.MULTI_PERL:
            skip("not on MULTI_PERL...")
        else:
            perl.eval("sub foo_elem { shift->{foo} }")
            hash = perl.eval("{ foo => 42 }")
            self.assertEquals(perl.call("foo_elem", hash), 42)

    def test_trap_exceptions(self):
        # try to trap exceptions
        try:
            perl.eval("die 'Oops!'")
        except perl.PerlError, val:
	    self.assertEquals(str(val)[:5],"Oops!")

        try:
            perl.call("not_there", 3, 4)
        except perl.PerlError, val:
            self.assertEquals(str(val), "Undefined subroutine &main::not_there called.\n")


    def test_function_scalar_context(self):
        # scalar context
        self.assertEquals(perl.call("foo2"), 42)

    def test_function_array_context_tuple_back(self):
        res = perl.call_tuple("foo2")
        self.assertEquals(len(res), 3)
        self.assertEquals(res[0], 1)
	self.assertEquals(res[1], 2)
	self.assertEquals(res[2], 3)

    def test_anonymous_perl_functions(self):
        # can we call anonymous perl functions
        # can we pass hashes both ways
        if perl.MULTI_PERL:
            self.skip("not on MULTI_PERL...")
        else:
            func = perl.eval("sub { $_[0] + $_[1] }")
            self.assertEquals(int(func(3, 4)), 7)

def test_main():
    from test import test_support
    test_support.run_unittest(TestPyPerlBasic)

if __name__ == "__main__":
    test_main()
