#!/usr/bin/make -f
INSTALL ?= install
PREFIX ?= /usr/local
MANPAGES ?= pybuild.1 dh_pypy.1 dh_python2.1 dh_python3.1
DVERSION=$(shell dpkg-parsechangelog | sed -rne 's,^Version: (.+),\1,p' || echo 'DEVEL')
VERSION=$(shell dpkg-parsechangelog | sed -rne 's,^Version: ([^-]+).*,\1,p' || echo 'DEVEL')

clean:
	make -C tests clean
	make -C pydist clean
	find . -name '*.py[co]' -delete
	find . -name __pycache__ -type d | xargs rm -rf
	rm -f .coverage $(MANPAGES)

dist:
	git archive --format=tar --prefix=dh-python-$(VERSION)/ HEAD \
	| xz -9 -c >../dh-python_$(VERSION).orig.tar.xz

install:
	$(INSTALL) -m 755 -d $(DESTDIR)$(PREFIX)/bin \
		$(DESTDIR)$(PREFIX)/share/debhelper/autoscripts/ \
		$(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Sequence/ \
		$(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Buildsystem/ \
		$(DESTDIR)$(PREFIX)/share/dh-python/dhpython/build
	$(INSTALL) -m 644 dhpython/*.py $(DESTDIR)$(PREFIX)/share/dh-python/dhpython/
	$(INSTALL) -m 644 dhpython/build/*.py $(DESTDIR)$(PREFIX)/share/dh-python/dhpython/build/
	$(INSTALL) -m 755 pybuild $(DESTDIR)$(PREFIX)/share/dh-python/
	$(INSTALL) -m 755 dh_pypy $(DESTDIR)$(PREFIX)/share/dh-python/
	$(INSTALL) -m 755 dh_python2 $(DESTDIR)$(PREFIX)/share/dh-python/
	$(INSTALL) -m 755 dh_python3 $(DESTDIR)$(PREFIX)/share/dh-python/
	sed -i -e 's/DEVELV/$(DVERSION)/' $(DESTDIR)$(PREFIX)/share/dh-python/pybuild
	sed -i -e 's/DEVELV/$(DVERSION)/' $(DESTDIR)$(PREFIX)/share/dh-python/dh_pypy
	sed -i -e 's/DEVELV/$(DVERSION)/' $(DESTDIR)$(PREFIX)/share/dh-python/dh_python2
	sed -i -e 's/DEVELV/$(DVERSION)/' $(DESTDIR)$(PREFIX)/share/dh-python/dh_python3
	
	$(INSTALL) -m 644 dh/pybuild.pm $(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Buildsystem/
	$(INSTALL) -m 644 dh/pypy.pm $(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Sequence/
	$(INSTALL) -m 644 dh/python2.pm $(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Sequence/
	$(INSTALL) -m 644 dh/python3.pm $(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Sequence/
	$(INSTALL) -m 644 autoscripts/* $(DESTDIR)$(PREFIX)/share/debhelper/autoscripts/

%.1: %.rst
	rst2man $< > $@

manpages: $(MANPAGES)

dist_fallback:
	make -C pydist $@

# TESTS
nose:
	nosetests3 --verbose --with-doctest --with-coverage

tests: nose
	make -C tests

test%:
	make -C tests $@

.PHONY: clean tests test% check_versions
