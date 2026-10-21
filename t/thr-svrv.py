import sys
import time

try:
    import threading
except ImportError:
    print("1..0")
    sys.exit(0)

import perl
if not perl.MULTI_PERL:
    print("1..0")
    sys.exit(0)

# This tests behaviour of perl objects passed from one
# thread (and perl interpreter) to the next one and that
# it is still destructed properly.

print("1..4")
sys.stdout.flush()

perl.eval("""
$| = 1;
sub Foo::hello { return "Hello" }
sub Foo::DESTROY { $main::destroyed++ }
""")
perl_obj = perl.eval('bless {}, "Foo"')
wrong_thread = []

def t1():
    global perl_obj
    try:
        perl_obj.hello()
    except ValueError:
        wrong_thread.append(1)

    perl.eval("""$| = 1; sub Foo::DESTROY { print "ok 4\\n" }""")
    perl_obj = perl.get_ref("@")
    perl_obj.__class__ = "Foo"

t = threading.Thread(target=t1)
t.start()
t.join()

if not wrong_thread: print("not", end=' ')
print("ok 1")

# free-threaded Python destroys an object released by another thread a bit later
for i in range(100):
    if perl.eval("$main::destroyed"):
        break
    time.sleep(0.05)
if perl.eval("$main::destroyed") != 1: print("not", end=' ')
print("ok 2")

print("ok 3")
sys.stdout.flush()
perl_obj = None  # last reference: destroyed in t1's interpreter, which prints ok 4
