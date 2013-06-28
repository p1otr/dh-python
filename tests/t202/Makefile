#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	test -f debian/python-foo/usr/lib/python2.6/dist-packages/foo.py
	test -f debian/python-foo/usr/lib/python2.6/dist-packages/bar/bar.py
	grep -q pycompile debian/python-foo/DEBIAN/postinst
	grep -q pyclean debian/python-foo/DEBIAN/prerm
