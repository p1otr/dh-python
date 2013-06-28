#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	# python2.4 hardcoded via `dh_python2 -shebang ...python2.4`
	grep -q '\-V 2.4 /usr/share/baz24' debian/foo/usr/share/python/runtime.d/foo.rtupdate
	grep -q '/usr/share/baz24 \-V 2.4' debian/foo/DEBIAN/postinst
	grep -q '#! /usr/bin/python2.4 -OO' debian/foo/usr/share/baz24/baz.py
	# python2.6 hardcoded via shebang
	grep -q '\-V 2.6 /usr/share/foo' debian/foo/usr/share/python/runtime.d/foo.rtupdate
	grep -q '/usr/share/foo \-V 2.6' debian/foo/DEBIAN/postinst
	# /env removed from shebang 
	grep -q '#! /usr/bin/python' debian/foo/usr/share/bar/bar.py
	# /local removed from shebang 
	grep -q '#! /usr/bin/python' debian/foo/usr/share/foo/baz.py
	grep -q '#! /usr/bin/python2.6' debian/foo/usr/share/foo/foo.py
