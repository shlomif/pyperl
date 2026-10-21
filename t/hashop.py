print("1..12")

import perl
h = perl.get_ref("%")

if h.__type__ != 'HASH' or h.__class__ != None: print("not ", end=' ')
print("ok 1")

if len(h) != 0 or len(list(h.items())) != 0 or \
   len(list(h.keys())) != 0 or len(list(h.values())) != 0:
    print("not ", end=' ')
print("ok 2")

try:
    print(h[42])
except TypeError as v:
    if str(v) != 'perl hash key must be string': print("not ", end=' ')
    print("ok 3")

try:
    print(h["foo"])
except KeyError as v:
    if str(v) != "'foo'": print("not ", end=' ')
    print("ok 4")

if h.get("foo") != None or h.get("foo", 42) != 42: print("not ", end=' ')
print("ok 5")

try:
    print(h.get(42))
except TypeError as v:
    if "int" not in str(v):
        print("not ", end=' ')
    print("ok 6")

h["foo"] = 42

if len(h) != 1 or h["foo"] != 42: print("not ", end=' ')
print("ok 7")

h["bar"] = 21

# perl hash order is random
if sorted(h.keys()) != ["bar", "foo"] or \
   sorted(h.values()) != [21, 42] or \
   sorted(h.items()) !=  [("bar", 21), ("foo", 42)]:
    print("not ", end=' ')
print("ok 8")

if "baz" in h or "bar" not in h: print("not ")
print("ok 9")

h2 = h.copy()
if id(h) == id(h2) or sorted(h.items()) != sorted(h2.items()): print("not ", end=' ')
print("ok 10")

h2.clear()
if len(h2) != 0: print("not ")
print("ok 11")

del h["bar"]
if list(h.keys()) != ["foo"]: print("not ", end=' ')
print("ok 12")

