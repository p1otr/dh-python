#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	grep -q python2.6 debian/foo/usr/share/foo/foo.py
	grep -q Depends:.*python2.6 debian/foo/DEBIAN/control
	#grep -q python2.5 debian/foo/usr/share/bar/bar.py
	#grep -q Depends:.*python2.5 debian/foo/DEBIAN/control
	grep -q python2.4 debian/foo/usr/share/foo/baz.py
	test ! -x debian/foo/usr/share/foo/baz.py
	grep -q Depends:.*python2.4 debian/foo/DEBIAN/control && false || true
