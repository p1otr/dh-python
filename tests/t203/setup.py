#!/usr/bin/env python
from distutils.core import setup, Extension
setup(name="distutils-test",
      version = "0.1",
      author="jbailey",
      author_email="jbailey@debian.org",
      url="http://www.python.org/sigs/distutils-sig/",
      ext_modules=[Extension('foo/bar', ['lib/bar.c'])],
      #py_modules=['package'],
      packages = ["foo"],
      package_dir = {'foo': 'lib'}
     )

