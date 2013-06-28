#!/usr/bin/make -f

include ../common.mk
DPY=$(DEBPYTHON_DEFAULT)

check:
	grep -q "pycompile -p python-foo /usr/lib/python-foo -V $(DPY)"\
		debian/python-foo/DEBIAN/postinst
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/bar.so
	test ! -f debian/python-foo/usr/share/pyshared/foo/bar.so
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/spam.so
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/spam.so.0.1
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/baz.so
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/baz.so.0.1
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/baz.so.0.1.2
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so.0
	test ! -L debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so.0
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so.0.0.0

clean: clean-common
	rm -rf lib/Foo.egg-info build
