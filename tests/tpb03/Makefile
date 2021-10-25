#!/usr/bin/make -f
include ../common.mk

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	test -f debian/python-foo/usr/lib/python2.7/dist-packages/foo.py
	grep -q 'Depends:.*python3-ply' debian/python3-foo/DEBIAN/control
	grep -q 'Depends:.*python-ply' debian/python-foo/DEBIAN/control

clean:
	./debian/rules clean
