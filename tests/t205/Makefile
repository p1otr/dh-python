#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	# test dh_python2
	test -f debian/python-foo/usr/share/pyshared/keep_this_one/__init__.py
	test ! -f debian/python-foo/usr/share/pyshared/remove_this_one/__init__.py
	test ! -f debian/python-foo/usr/share/pyshared/foo/__init__.py
	grep -q remove_this_one debian/python-foo/usr/share/python/ns/python-foo
	grep -q foo debian/python-foo/usr/share/python/ns/python-foo
	grep -q bar.baz debian/python-foo/usr/share/python/ns/python-foo
	grep -q keep_this_one debian/python-foo/usr/share/python/ns/python-foo && false || true
	grep -q "pycompile -p python-foo" debian/python-foo/DEBIAN/postinst
	grep -q "pyclean -p python-foo" debian/python-foo/DEBIAN/prerm
	# test pycompile
#	DESTDIR=debian/python-foo/ ../../pycompile -v debian/python-foo/usr/lib/
#	set -e; for i in remove_this_one bar bar/baz;\
#	do [ "`ls debian/python-foo/usr/lib/python2.*/*-packages/$$i/__init__.py | wc -l`" != '0' ];\
#	[ "`ls debian/python-foo/usr/lib/python2.*/*-packages/$$i/__init__.pyc | wc -l`" != '0' ];\
#	done
	# test pyclean
#	DESTDIR=debian/python-foo/ ../../pyclean -v debian/python-foo/usr/lib/
#	set -e; for i in remove_this_one bar bar/baz;\
#	do [ "`ls debian/python-foo/usr/lib/python2.*/*-packages/$$i/__init__.py 2>/dev/null || true | wc -l`" = 0 ];\
#	[ "`ls debian/python-foo/usr/lib/python2.*/*-packages/$$i/__init__.pyc 2>/dev/null || true | wc -l`" = 0 ];\
#	done
