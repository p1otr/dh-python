#!/usr/bin/make -f

export DEBPYTHON_DEFAULT ?= $(shell python3 ../../dhpython/_defaults.py default cpython2)
export DEBPYTHON_SUPPORTED ?= $(shell python3 ../../dhpython/_defaults.py supported cpython2)
export DEBPYTHON3_DEFAULT ?= $(shell python3 ../../dhpython/_defaults.py default cpython3)
export DEBPYTHON3_SUPPORTED ?= $(shell python3 ../../dhpython/_defaults.py supported cpython3)
export DEBPYPY_DEFAULT ?= $(shell python3 ../../dhpython/_defaults.py default pypy)
export DEBPYPY_SUPPORTED ?= $(shell python3 ../../dhpython/_defaults.py supported pypy)
export DEB_HOST_MULTIARCH=my_multiarch-triplet
export DEB_HOST_ARCH ?= $(shell dpkg-architecture -qDEB_HOST_ARCH)

all: run check

run: clean
	dpkg-buildpackage -b -us -uc

clean-common:
	./debian/rules clean
