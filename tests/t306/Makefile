#!/usr/bin/make -f
include ../common.mk

all: run check

run: clean
	dpkg-buildpackage -b -us -uc

check:
	grep -qe "^Depends: .*python3\(:any\)\? (<< 3\.[0-9]\+)" \
		debian/foo/DEBIAN/control
	grep -qe "^Depends: .*python3\(:any\)\? (>= 3\.[0-9]\+~)" \
		debian/foo/DEBIAN/control

clean:
	./debian/rules clean
	rm -rf lib/Foo.egg-info build
