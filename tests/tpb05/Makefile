#!/usr/bin/make -f
include ../common.mk

DI=debian/python3-foo/usr/lib/python3/dist-packages/foo-0.1.dist-info

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo/__init__.py
	grep -q ^foo/__init__.py, $(DI)/RECORD
	test ! -f $(DI)/direct_url.json
	grep -L ^foo-0.1.dist-info/direct_url.json, $(DI)/RECORD | grep -q RECORD
	grep -q 'Depends:.*python3-tomli' debian/python3-foo/DEBIAN/control
	grep -q 'Depends:.*python3-importlib-metadata \| python3 (>> 3\.5)' debian/python3-foo/DEBIAN/control
	grep -L 'Depends:.*tox' debian/python3-foo/DEBIAN/control | grep -q control
	find .pybuild -name test-executed | grep -q test-executed
	grep -q usr/bin/python3$$ debian/python3-foo/usr/bin/foo

clean:
	./debian/rules clean
