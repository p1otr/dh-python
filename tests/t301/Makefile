#!/usr/bin/make -f
include ../common.mk

check:
	grep -qe "Depends: .*python3\(:any\)\? (<< 3.9)" debian/python3-foo/DEBIAN/control
	grep -q "Recommends: .*python3-mako" debian/python3-foo/DEBIAN/control
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo/__init__.py
	test ! -f debian/python3-foo/usr/lib/python3/dist-packages/foo/spam.py
	grep -q 'py3compile -p python3-foo -V 3\.1-3\.9' debian/python3-foo/DEBIAN/postinst
	grep -q 'pypy3compile -p python3-foo -V 3\.1-3\.9' debian/python3-foo/DEBIAN/postinst
	grep -q 'py3clean -p python3-foo\s*$$' debian/python3-foo/DEBIAN/prerm

clean:
	./debian/rules clean
	rm -rf lib/Foo.egg-info
