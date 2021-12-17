#!/usr/bin/make -f
include ../common.mk

check:
	grep -q "py3compile -p python3-foo:$(DEB_HOST_ARCH) /usr/lib/python3-foo"\
		debian/python3-foo/DEBIAN/postinst
	grep -q "pypy3compile -p python3-foo:$(DEB_HOST_ARCH) /usr/lib/python3-foo"\
		debian/python3-foo/DEBIAN/postinst
	grep -q "py3clean -p python3-foo:$(DEB_HOST_ARCH)" debian/python3-foo/DEBIAN/prerm
	[ "`find debian/python3-foo/usr/lib/python3/dist-packages/foo -name 'bar.cpython-*.so'`" != "" ]
	test -e debian/python3-foo/usr/lib/python3-foo/empty-private-dir
	test ! -e debian/python3-foo/usr/lib/python3/dist-packages/empty-public-dir
	# test if moved from include/python3.X/ to include/python3.Xm/ (for Python << 3.8)
	#test -f debian/python3-foo/usr/include/python$(DEBPYTHON3_DEFAULT)m/foo.h

clean:
	./debian/rules clean
	rm -rf lib/Foo.egg-info build
