#!/usr/bin/make -f

include ../common.mk
DPY=$(DEBPYTHON_DEFAULT)
ifeq ($(DPY),2.7) 
TRIPLET=.$(DEB_HOST_MULTIARCH)
endif

check:
	grep -q "pycompile -p python-foo:$(DEB_HOST_ARCH) /usr/lib/python-foo -V $(DPY)"\
		debian/python-foo/DEBIAN/postinst
	grep -q "pyclean -p python-foo:$(DEB_HOST_ARCH) /usr/lib/python-foo -V $(DPY)"\
		debian/python-foo/DEBIAN/prerm
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/bar$(TRIPLET).so
	test ! -f debian/python-foo/usr/share/pyshared/foo/bar.so
	test ! -f debian/python-foo/usr/share/pyshared/foo/bar$(TRIPLET).so
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/spam$(TRIPLET).so
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/spam.so.0.1
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/baz$(TRIPLET).so
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/baz.so.0.1
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/baz.so.0.1.2
	test -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux$(TRIPLET).so
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so.0
	test ! -L debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so.0
	test ! -f debian/python-foo/usr/lib/python${DPY}/dist-packages/foo/quux.so.0.0.0

clean: clean-common
	rm -rf lib/Foo.egg-info build
