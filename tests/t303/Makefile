#!/usr/bin/make -f
include ../common.mk

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	test ! -d debian/python3-foo/usr/lib/python3.*/site-packages
	grep -q 'py3compile -p python3-foo\s*$$' debian/python3-foo/DEBIAN/postinst
	grep -q 'pypy3compile -p python3-foo\s*||\s*true$$' debian/python3-foo/DEBIAN/postinst
	grep -q 'py3clean -p python3-foo\s*$$' debian/python3-foo/DEBIAN/prerm

clean:
	./debian/rules clean
