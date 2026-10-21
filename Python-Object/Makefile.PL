use ExtUtils::MakeMaker;
use Config;

my $python = $ENV{PYTHON} || 'python';
chomp(my $pyinc = `$python -c "import sysconfig; print('-I' + sysconfig.get_paths()['include'])"`);
chomp(my $pylib = `$python -c "import sysconfig; print(sysconfig.get_config_var('BLDLIBRARY') or '')"`);
chomp(my $pysitelib = `$python -c "import sysconfig; print(sysconfig.get_paths()['platlib'])"`);


my @define;
my @libs;

push(@define, "MULTI_PERL") if -f "../MULTI_PERL" && $Config{useithreads};

push(@libs, $pylib);

if (-f "../BOOT_FROM_PERL") {
    push(@define, "BOOT_FROM_PERL");
    push(@extra, OBJECT => "Object.o $pysitelib/perl.so");
}

if (@define) {
    push(@extra, DEFINE => join(" ", map "-D$_", @define));
}
push(@extra, LIBS => \@libs) if @libs;

WriteMakefile(
    NAME	 => 'Python::Object',
    VERSION_FROM => 'lib/Python/Object.pm',
    INC          => $pyinc,
    @extra,
    dist         => { COMPRESS => 'xz -9f', SUFFIX => 'xz', },
);
