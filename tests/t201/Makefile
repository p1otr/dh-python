#!/usr/bin/make -f

include ../common.mk
DPY=$(DEBPYTHON_DEFAULT)

check:
	grep -q "Recommends: .*python-mako" debian/python-foo/DEBIAN/control
	#grep -q 'python-foo (>= 2:0.1~rc2)' debian/python-foo/DEBIAN/control
	test -f debian/python-foo/usr/lib/python2.6/dist-packages/foo/__init__.py
	test ! -f debian/python-foo/usr/lib/python2.6/dist-packages/foo/spam.py
	grep -q "Depends: .*python (<<" debian/python-foo/DEBIAN/control
	[ "`readlink debian/python-foo/usr/lib/python$(DPY)/dist-packages/foo/absolute_link_to_tmp`" = "/tmp" ]
	[ "`readlink debian/python-foo/usr/lib/python$(DPY)/dist-packages/foo/link_to_parent_dir`" = ".." ]

clean: clean-common
	rm -rf lib/Foo.egg-info
