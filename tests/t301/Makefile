#!/usr/bin/make -f
include ../common.mk

all: run check


run: clean
	dpkg-buildpackage -b -us -uc

check:
	grep -qe "Depends: .*python3\(:any\)\? (<< 3.7)" debian/python3-foo/DEBIAN/control
	grep -q "Recommends: .*python3-mako" debian/python3-foo/DEBIAN/control
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo/__init__.py
	test ! -f debian/python3-foo/usr/lib/python3/dist-packages/foo/spam.py

clean:
	./debian/rules clean
	rm -rf lib/Foo.egg-info
