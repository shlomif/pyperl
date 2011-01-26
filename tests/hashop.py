#!/usr/bin/env python

import unittest
import perl

class TestPyPerlHashOp(unittest.TestCase):

    def setUp(self):
        self.h = perl.get_ref("%")

    def test_type_is_hash(self):
        self.assertEquals(self.h.__type__, 'HASH')
        self.assertEquals(self.h.__class__, None)

    def test_hash_elements(self):
        self.assertEquals(len(self.h), 0)
        self.assertEquals(len(self.h.items()), 0)
        self.assertEquals(len(self.h.keys()), 0)
        self.assertEquals(len(self.h.values()), 0)


    def test_hash_type_error(self):
        try:
            print self.h[42]
        except TypeError, v:
            self.assertEquals(str(v), 'perl hash key must be string')

    def test_hash_key_error(self):
        try:
            print self.h["foo"]
        except KeyError, v:
            self.assertEquals(str(v), "'foo'")

    def test_hash_get(self):
        self.h["foo"] = 42
        self.assertIsNotNone(self.h.get("foo"))
        self.assertEquals(self.h.get("foo"), 42)

    def test_hash_get_type_error(self):
        try:
            print self.h.get(42)
        except TypeError, v:
            self.assertEquals(str(v), "must be string or read-only buffer, not int")

    def test_hash_key_index(self):
        self.h["foo"] = 42
        self.assertEquals(len(self.h), 1)
        self.assertEquals(self.h["foo"], 42)

    def test_hash_algoritm_order(self):
        self.h["foo"] = 42
        self.h["bar"] = 21

        # self.here we assume a certain order, which might get broken by another self.hash
        # algoritim or other internal changes.  In that case fix the tests below.
        self.assertEquals(self.h.keys(), ["bar", "foo"])
        self.assertEquals(self.h.values(), [21, 42])
        self.assertEquals(self.h.items(), [("bar", 21), ("foo", 42)])

    def test_hash_has_key(self):
        self.h["bar"] = 21

        self.assertFalse(self.h.has_key("baz"))
        self.assertTrue(self.h.has_key("bar"))

    def test_hash_copy(self):
        self.h2 = self.h.copy()
        self.assertNotEquals(id(self.h), id(self.h2))
        self.assertEquals(self.h.items(), self.h2.items())

    def test_hash_clear(self):
        self.h2 = self.h.copy()
        self.h2.clear()
        self.assertEquals(len(self.h2), 0)

    def test_hash_delete(self):
        self.h["foo"] = 42
        self.h["bar"] = 21
        del self.h["bar"]
        self.assertEquals(self.h.keys(), ["foo"])

def test_main():
    from test import test_support
    test_support.run_unittest(TestPyPerlHashOp)

if __name__ == "__main__":
    test_main()
