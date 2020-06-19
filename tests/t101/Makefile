#!/usr/bin/make -f
include ../common.mk

check:
	test -f debian/pypy-foo/usr/lib/pypy/dist-packages/foo.py
	test ! -d debian/pypy-foo/usr/lib/pypy/site-packages
	test ! -d debian/pypy-foo/usr/lib/pypy/dist-packages/__pycache__
	grep -q pypycompile debian/pypy-foo/DEBIAN/postinst
	grep -q pypyclean debian/pypy-foo/DEBIAN/prerm

clean:
	./debian/rules clean
