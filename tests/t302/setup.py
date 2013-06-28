#! /usr/bin/python3
from distutils.core import setup, Extension

setup(name='Foo',
      version='0.1',
      description="package with Python extension",
      author='Piotr Ożarowski',
      author_email='piotr@debian.org',
      url='http://www.debian.org/',
      ext_modules=[Extension('foo/bar', ['lib/bar.c'])],
      #py_modules=['package'],
      packages=['foo'],
      package_dir={'foo': 'lib'})
