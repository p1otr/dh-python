#!/usr/bin/make -f
include ../common.mk

DI=debian/python3-foo/usr/lib/python3/dist-packages/foo-0.1.dist-info

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	grep -q ^foo.py, $(DI)/RECORD
	test ! -f $(DI)/direct_url.json
	grep -L ^foo-0.1.dist-info/direct_url.json, $(DI)/RECORD | grep -q RECORD

clean:
	./debian/rules clean
