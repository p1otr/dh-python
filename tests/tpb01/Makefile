#!/usr/bin/make -f
include ../common.mk

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	grep -q 'Depends:.*python3-tomli' debian/python3-foo/DEBIAN/control

clean:
	./debian/rules clean
