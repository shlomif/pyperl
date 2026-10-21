#!/usr/bin/env python

import unittest
import perl


class TestPyPerlUnicode(unittest.TestCase):

    def setUp(self):
        self.ident = perl.eval("sub { $_[0] }")
        self.length = perl.eval("sub { length $_[0] }")

    def test_str_is_characters_in_perl(self):
        s = "héllo €"
        self.assertEqual(self.length(s), 7)
        self.assertEqual(self.ident(s), s)
        self.assertEqual(self.length("ascii"), 5)

    def test_perl_character_strings(self):
        self.assertEqual(perl.eval('"héllo"'), "héllo")
        self.assertEqual(perl.eval('length "héllo"'), 5)
        self.assertEqual(perl.eval('my $s = chr(233); utf8::upgrade($s); $s'), "é")
        self.assertEqual(perl.eval('"\\x{263a}"'), "☺")

    def test_perl_byte_strings(self):
        self.assertEqual(perl.eval("chr(233)"), b"\xe9")
        self.assertEqual(perl.eval('require Encode; Encode::encode_utf8("\\x{e9}")'), b"\xc3\xa9")
        self.assertEqual(perl.eval('pack("C*", 0x80, 0xff, 0)'), b"\x80\xff\x00")
        self.assertEqual(self.ident(b"\x80\xff"), b"\x80\xff")
        self.assertEqual(self.length(b"\xc3\xa9"), 2)

    def test_hash_keys(self):
        h = perl.get_ref("%")
        h["clé"] = 1
        self.assertEqual(perl.eval('sub { join ",", map length, keys %{$_[0]} }')(h), "3")
        self.assertEqual(h["clé"], 1)
        self.assertTrue("clé" in h)
        self.assertEqual(h.get("clé"), 1)
        self.assertEqual(list(h.keys()), ["clé"])
        h2 = perl.eval('{ "clé" => 2, "\\x{263a}" => 3 }')
        self.assertEqual(sorted(h2.keys()), ["clé", "☺"])
        self.assertEqual(h2["☺"], 3)

    def test_error_message(self):
        with self.assertRaises(perl.PerlError) as cm:
            perl.eval('die "héllo\\n"')
        self.assertEqual(str(cm.exception), "héllo\n")

    def test_python_str_seen_from_perl(self):
        class Obj:
            def __str__(self):
                return "über"
        self.assertEqual(perl.eval('sub { length "$_[0]" }')(Obj()), 4)

    def test_apply_keyword_names(self):
        f = perl.eval('use Python qw(apply); sub { apply($_[0], undef, { "clé" => 1 }) }')
        self.assertEqual(f(lambda **kw: list(kw)), ["clé"])


if __name__ == "__main__":
    unittest.main()
