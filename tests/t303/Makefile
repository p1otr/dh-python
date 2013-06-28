#!/usr/bin/make -f
include ../common.mk

all: run check

run: clean
	dpkg-buildpackage -b -us -uc

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	test ! -d debian/python3-foo/usr/lib/python3.*/site-packages

clean:
	./debian/rules clean
