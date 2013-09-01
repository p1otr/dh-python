# A debhelper build system class for building Python libraries
#
# Copyright: © 2012-2013 Piotr Ożarowski

# TODO:
# * support for dh --parallel

package Debian::Debhelper::Buildsystem::pybuild;

use strict;
use Debian::Debhelper::Dh_Lib qw(error doit);
use base 'Debian::Debhelper::Buildsystem';

sub DESCRIPTION {
	"Python pybuild"
}

sub check_auto_buildable {
	my $this=shift;
	return doit('pybuild', '--detect', '--really-quiet', '--dir', $this->get_sourcedir());
}

sub new {
	my $class=shift;
	my $this=$class->SUPER::new(@_);
	$this->enforce_in_source_building();

	if (!$ENV{'PYBUILD_INTERPRETERS'}) {
		$this->{pydef} = `pyversions -vd 2>/dev/null`;
		$this->{pydef} =~ s/\s+$//;
		$this->{pyvers} = `pyversions -vr 2>/dev/null`;
		$this->{pyvers} =~ s/\s+$//;
		$this->{py3def} = `py3versions -vd 2>/dev/null`;
		$this->{py3def} =~ s/\s+$//;
		$this->{py3vers} = `py3versions -vr 2>/dev/null`;
		$this->{py3vers} =~ s/\s+$//;
		$this->{pypydef} = `pypy -c 'from sys import pypy_version_info as i; print("%s.%s" % (i.major, i.minor))' 2>/dev/null`;
		$this->{pypydef} =~ s/\s+$//;
	}

	return $this;
}

sub configure {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('configure', @_)) {
		doit(@$command, '--dir', $this->get_sourcedir());
	}
}

sub build {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('build', @_)) {
		doit(@$command, '--dir', $this->get_sourcedir());
	}
}

sub install {
	my $this=shift;
	my $destdir=shift;
	foreach my $command ($this->pybuild_commands('install', @_)) {
		doit(@$command, '--dir', $this->get_sourcedir(), '--dest-dir', $destdir);
	}
}

sub test {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('test', @_)) {
		doit(@$command, '--dir', $this->get_sourcedir());
	}
}

sub clean {
	my $this=shift;
	foreach my $command ($this->pybuild_commands('clean', @_)) {
		doit(@$command, '--dir', $this->get_sourcedir());
	}
	doit('rm', '-rf', '.pybuild/');
	doit('find', '.', '-name', '*.pyc', '-exec', 'rm', '{}', ';');
}

sub pybuild_commands {
	my $this=shift;
	my $step=shift;
	my @options = @_;
	my @result;

	if ($ENV{'PYBUILD_INTERPRETERS'}) {
		push @result, ['pybuild', "--$step", @options];
	}
	else {
		# get interpreter packages from Build-Depends{,-Indep}:
		# NOTE: possible problems with alternative/versioned dependencies
		my @deps = $this->python_build_dependencies();

		my $pyall = 0;
		my $pyalldbg = 0;
		my $py3all = 0;
		my $py3alldbg = 0;

		my $i = 'python{version}';

		# Python
		if ($this->{pyvers}) {
			if (grep {$_ eq 'python-all' or $_ eq 'python-all-dev'} @deps) {
				$pyall = 1;
				push @result, ['pybuild', "--$step", '-i', $i, '-p', $this->{pyvers}, @options];
			}
			if (grep {$_ eq 'python-all-dbg'} @deps) {
				$pyalldbg = 1;
				push @result, ['pybuild', "--$step", '-i', "$i-dbg", '-p', $this->{pyvers}, @options];
			}
		}
		if ($this->{pydef}) {
			if (not $pyall and grep {$_ eq 'python' or $_ eq 'python-dev'} @deps) {
				push @result, ['pybuild', "--$step", '-i', $i, '-p', $this->{pydef}, @options];
			}
			if (not $pyalldbg and grep {$_ eq 'python-dbg'} @deps) {
				push @result, ['pybuild', "--$step", '-i', "$i-dbg", '-p', $this->{pydef}, @options];
			}
		}

		# Python 3
		if ($this->{py3vers}) {
			my $i = 'python{version}';
			if (grep {$_ eq 'python3-all' or $_ eq 'python3-all-dev'} @deps) {
				$py3all = 1;
				push @result, ['pybuild', "--$step", '-i', $i, '-p', $this->{py3vers}, @options];
			}
			if (grep {$_ eq 'python3-all-dbg'} @deps) {
				$py3alldbg = 1;
				push @result, ['pybuild', "--$step", '-i', "$i-dbg", '-p', $this->{py3vers}, @options];
			}
		}
		if ($this->{py3def}) {
			if (not $py3all and grep {$_ eq 'python3' or $_ eq 'python3-dev'} @deps) {
 				# TODO: "python3" case: should X-Python3-Version header in debian/control be also required here?
				push @result, ['pybuild', "--$step", '-i', $i, '-p', $this->{py3def}, @options];
			}
			if (not $py3alldbg and grep {$_ eq 'python3-dbg'} @deps) {
				push @result, ['pybuild', "--$step", '-i', "$i-dbg", '-p', $this->{py3def}, @options];
			}
		}
		# TODO: pythonX.Y → `pybuild -i python{version} -p X.Y`

		# PyPy
		if ($this->{pypydef} and grep {$_ eq 'pypy'} @deps) {
			push @result, ['pybuild', "--$step", '-i', 'pypy', '-p', $this->{pypydef}, @options];
		}
	}
	return @result;
}

sub python_build_dependencies {
	my $this=shift;

	my @result;
	open (CONTROL, 'debian/control') || error("cannot read debian/control: $!\n");
	foreach my $builddeps (join('', <CONTROL>) =~ 
			/^Build-Depends[^:]*:.*\n(?:^[^\w\n#].*\n)*/gmi) {
		while ($builddeps =~ /[\s,](pypy|python[0-9\.]*(-all)?((-dev)|(-dbg))?)[\s,]|$/g) {
			if ($1) {push @result, $1};
		}
	}

	close CONTROL;
	return @result;
}

1
