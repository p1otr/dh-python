#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	test -f debian/python-foo/usr/lib/python2.7/dist-packages/foo.py
	test -f debian/python-foo/usr/lib/python2.7/dist-packages/bar/bar.py
	test \! -f debian/python-foo/usr/lib/python2.7/dist-packages/tests/__init__.py
	grep -q 'pycompile -p python-foo\s*$$' debian/python-foo/DEBIAN/postinst
	grep -q 'pyclean -p python-foo\s*$$' debian/python-foo/DEBIAN/prerm
