#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	# python2.4 hardcoded via `dh_python2 -V 2.4`
	grep -q Depends:.*python2.4 debian/foo/DEBIAN/control
	grep -q '\-V 2.4 /usr/share/baz24' debian/foo/usr/share/python/runtime.d/foo.rtupdate
	grep -q '/usr/share/baz24 \-V 2.4' debian/foo/DEBIAN/postinst
	# python2.5 due to X-Python-Version: 2.5
	#grep -q Depends:.*python2.5 debian/foo/DEBIAN/control
	# python2.6 hardcoded via shebang - test ignored as 2.6 is no longer supported
	#grep -q Depends:.*python2.6 debian/foo/DEBIAN/control
	grep -q '\-V 2.6 /usr/share/foo' debian/foo/usr/share/python/runtime.d/foo.rtupdate
	grep -q '/usr/share/foo \-V 2.6' debian/foo/DEBIAN/postinst
	# python2 shebang
	grep -q Depends:.*python2 debian/foo/DEBIAN/control
	grep -q '#! /usr/bin/python2' debian/foo/usr/bin/egg
