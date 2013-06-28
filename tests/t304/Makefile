#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	# python3.2 hardcoded via `dh_python3 --shebang ...python3.2`
	grep -q '#! /usr/bin/python3.2 -OO' debian/foo/usr/share/baz32/baz.py
	# python3.3 hardcoded via shebang
	grep -q '/usr/share/foo \-V 3.3' debian/foo/DEBIAN/postinst
	# /env removed from shebang 
	grep -q '#! /usr/bin/python3' debian/foo/usr/share/bar/bar.py
	# /local removed from shebang 
	grep -q '#! /usr/bin/python3' debian/foo/usr/share/foo/baz.py
	grep -q '#! /usr/bin/python3.3' debian/foo/usr/share/foo/foo.py
