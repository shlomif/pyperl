#!/usr/bin/env python3

from setuptools import setup, Extension
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext
try:
    from setuptools.command.build import build
except ImportError:  # setuptools < 62.4
    from distutils.command.build import build
import sysconfig
import os

DEBUG = 0
perl = 'perl'

import os
import sys
import subprocess
if subprocess.run([perl, "-e", "exit($] < 5.010001)"]).returncode != 0:
    sys.exit("pyperl needs perl 5.10.1 or newer")

MULTI_PERL = os.path.isfile("MULTI_PERL")
if MULTI_PERL and subprocess.run([perl, "-MConfig", "-e", "print $Config{useithreads} ? 1 : 0"],
                                 stdout=subprocess.PIPE, universal_newlines=True).stdout.strip() != "1":
    print("MULTI_PERL ignored: perl is built without ithreads")
    MULTI_PERL = False
BOOT_FROM_PERL = os.path.isfile("BOOT_FROM_PERL")
WIN32 = sys.platform == "win32"

def perl_config(name):
    return subprocess.run([perl, "-MConfig", "-e", "print $Config{%s}" % name],
                          stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()

def opt_split(opts):
    return [x.replace('"', '') for x in opts.split()]  # Strawberry quotes paths

p = os.popen(perl + ' ./opts.pl')
perl_ccopts = p.readline().strip()
perl_ldopts = p.readline().strip()
p.close()

ext_name     = "perl"
include_dirs = []
macros       = []
cc_extra     = []

for x in opt_split(perl_ccopts):
    if x[:2] == '-I':
        include_dirs.append(x[2:])

    # XXX This is disabled since distutils does not yet implement
    # define_macros.  Aarghhh!!  So much time wasted on debugging
    # because of this.
    elif 0 and x[:2] == '-D':
        m = x[2:].split('=', 2)
        if len(m) == 1:
            m.append(None)
        macros.append(tuple(m))
    else:
        cc_extra.append(x)

lib_dirs  = []
libs      = []
ld_extra  = []
o_extra   = []
sym_extra   = []

extra_ext = []

if not WIN32:
    ld_extra.extend(perl_ldopts.split())

sources = ['perlmodule.c',
        'lang_lock.c',
        'lang_map.c',
        'svrv_object.c',
        'pyo.c',
        'try_perlapi.c',
        ]

if BOOT_FROM_PERL:
    cc_extra.append("-DBOOT_FROM_PERL")
else:
    for x in opt_split(perl_ldopts):
        if x[:2] == '-L':
            lib_dirs.append(x[2:])
        elif x[:2] == '-l' and sys.platform != 'win32':
            libs.append(x[2:])
        elif x[:1] != '-' and (x[-3:] == '.so' or
                x[-2:] == '.o'  or
                x[-2:] == '.a'
                ):
            o_extra.append(x)
        else:
            ld_extra.append(x)

    if not os.path.isfile("perlxsi.c"):
        os.system(perl + " -MExtUtils::Embed -e xsinit")
    sources.append('perlxsi.c');

    # Try to figure out if we use dlopen on this platform
    p = os.popen(perl + ' -V:dlsrc')
    dlsrc = p.readline()
    p.close()
    if dlsrc == "dlsrc='dl_dlopen.xs';\n":
        ext_name = "perl2"
        cc_extra.append('-DDL_HACK')
        cc_extra.append('-DEXT_SUFFIX="' + sysconfig.get_config_vars().get("EXT_SUFFIX", ".so") + '"')
        extra_ext.append(Extension(name = "perl",
            extra_compile_args = cc_extra,
            sources = ["dlhack.c"],
            libraries= ["dl"],
            ))


if MULTI_PERL:
    cc_extra.append("-DMULTI_PERL")
    sources.append('thrd_ctx.c')

if not os.path.isfile("try_perlapi.c") or \
        os.path.getmtime("try_perlapi.c") < os.path.getmtime("try_perlapi.pl"):
            os.system(perl + " try_perlapi.pl")

if len(sys.argv) > 1 and sys.argv[1] in ("test", "build", "install"):
    cwd=os.getcwd()
    ldpath = '%s/Python-Object/blib/arch/auto/Python/Object' % cwd
    perllib = '%s/Python-Object/blib/lib' % cwd
    perlarchlib = '%s/Python-Object/blib/arch' % cwd
    os.environ["PERL5LIB"] = os.pathsep.join([perllib, perlarchlib] + ([os.environ["PERL5LIB"]] if "PERL5LIB" in os.environ else []))
    os.environ["LD_LIBRARY_PATH"] = "%s%s" % (ldpath, (":"+os.environ["LD_LIBRARY_PATH"] if "LD_LIBRARY_PATH" in os.environ else ''))

# Python-Object/Makefile.PL finds Python.h through this, also under pip
os.environ["PYTHON"] = sys.executable


if WIN32:
    # Python::Object is linked into the extension: a DLL cannot import from the .pyd that loads it
    with open(os.path.join("Python-Object", "lib", "Python", "Object.pm")) as f:
        xs_version = [l.split("'")[1] for l in f if l.startswith("$VERSION")][0]
    sources.append(os.path.join("Python-Object", "Object.c"))
    macros += [("XS_VERSION", '"%s"' % xs_version), ("VERSION", '"%s"' % xs_version)]
    if sys.maxsize > 2**32:
        macros.append(("MS_WIN64", None))

if DEBUG:
    print(("Macros:", macros))
    print(("Include: ", include_dirs))
    print(("Extra CC: ", cc_extra))
    print(("Obj: ", o_extra))
    print(("Libs:", libs))
    print(("Lib dirs:",  lib_dirs))
    print(("Extra LD: ", ld_extra))

ext_modules = []
ext_modules.append(Extension(name = ext_name,
    sources = sources,
    define_macros = macros,
    include_dirs = include_dirs,
    extra_compile_args = cc_extra,
    extra_objects =  o_extra,
    libraries = libs,
    library_dirs = lib_dirs,
    extra_link_args = ld_extra,
    export_symbols = sym_extra,
    ))
ext_modules.extend(extra_ext)

class build_ext_perl(build_ext):
    def initialize_options(self):
        build_ext.initialize_options(self)
        if WIN32 and perl_config("cc") == "gcc":
            self.compiler = "mingw32"  # perl's headers need the compiler perl was built with

class build_perl(build):
    def run(self):
        os.chdir('Python-Object')
        makefile_pl = [perl, 'Makefile.PL']
        # self-built perls have no vendor dirs
        vendorarch = subprocess.run([perl, '-MConfig', '-e', 'print $Config{installvendorarch}'],
                                    stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
        if vendorarch:
            makefile_pl.append('INSTALLDIRS=vendor')
        build.spawn(self, makefile_pl)
        make = perl_config("make") or "make"
        build.spawn(self, [make, 'pm_to_blib', 'Object.c'] if WIN32 else [make])
        os.chdir('..')
        build.run(self)
        # perlmodule.c puts this bundle on perl's @INC
        bundle = os.path.join(self.build_lib, 'pyperl-perl')
        for part in ('lib', 'arch'):
            if os.path.isdir(os.path.join('Python-Object', 'blib', part)):
                self.copy_tree(os.path.join('Python-Object', 'blib', part), bundle)
        if WIN32:
            # Python does not search PATH for perl5xx.dll
            perl_bin = perl_config("bin")
            with open(os.path.join(self.build_lib, 'pyperl-dll.pth'), 'w') as f:
                f.write("import os; os.path.isdir(%r) and os.add_dll_directory(%r)\n" % (perl_bin, perl_bin))

# a perl that boots python needs Python::Object in its own library
class boot_from_perl_install(install):

    def run(self):
        self.run_command('build')
        if self.root is None:
            self.root = ''

        os.chdir('Python-Object')
        install.spawn(self, ["make",] + (["DESTDIR=%s" % self.root] if len(self.root) else []) + ["install",])
        os.chdir('..')
        install.run(self)

setup (name        = "pyperl",
        version     = "1.0.4",
        description = "Embed a Perl interpreter",
        url         = "https://github.com/mgheorghe/pyperl",
        author      = "ActiveState",
        author_email= "gisle@ActiveState.com",
        python_requires = ">=3.6",
        py_modules  = ['dbi', 'dbi2', 'perlpickle', 'perlmod'],
        ext_modules = ext_modules,
        cmdclass    = dict(build=build_perl, build_ext=build_ext_perl,
                           **({'install': boot_from_perl_install} if BOOT_FROM_PERL else {})),
        test_suite  = "tests"
        )

# vim:ts=4:sw=4:et
