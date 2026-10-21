#!/usr/bin/env python

import sys
import os
import re

expect_re = re.compile(r"^1\.\.(\d+)$")
ok_re     = re.compile(r"^(not\s+)?ok\s+(\d+)$")

def test_ok(f):
    expect_next = None
    print(f, end='')
    for i in range(20 - len(f)):
        sys.stdout.write(".")
    sys.stdout.flush()

    # run from the top dir (tests "use lib 't'"), unbuffered
    p = os.popen('"%s" -u %s' % (sys.executable, os.path.join("t", f)))

    ok = 1

    while 1:
        line = p.readline()
        if not line: break
        #print line,

        res = expect_re.match(line)
        if res:
            expect_max  = int(res.group(1))
            if expect_max == 0:
                print(" skipped")
                p.close()
                return 1
            expect_next = 1
            continue

        if not (line.startswith("ok") or line.startswith("actually skipping")):
              ok = 0
              continue

        res = ok_re.match(line)
        if res:
            t = int(res.group(2))
            if t == expect_next:
                expect_next = expect_next + 1
            else:
                ok = 0
            continue
    if p.close():  # non-zero exit
        ok = 0
    if ok and (expect_next is None or (expect_next - 1) != expect_max):
        ok = 0

    if (ok): print(" ok")
    else:    print(" failed")
    return ok

files = os.listdir("t")
files.sort()

num_failed = 0
for f in files:
    if f[-3:] == '.py':
        if not test_ok(f):
            num_failed = num_failed + 1

print()
if num_failed:
    print(num_failed, "TESTS FAILED" + ("!" * num_failed))
    sys.exit(1)
else:
    print("All tests passed.")
