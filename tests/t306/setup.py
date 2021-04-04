#! /usr/bin/python3
from distutils.core import setup, Extension

setup(name='Foo',
      version='0.1',
      description="package with private Python extension",
      author='Maximilian Engelhardt',
      author_email='maxi@daemonizer.de',
      url='http://www.debian.org/',
      ext_modules=[Extension('foo/bar', ['lib/bar.c'])],
      packages=['foo'],
      package_dir={'foo': 'lib'})
