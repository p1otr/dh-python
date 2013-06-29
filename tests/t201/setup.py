#! /usr/bin/python
# -*- coding: UTF-8 -*-
from distutils.core import setup

setup(name='Foo',
      version='0.1',
      description="Foo to rule them all",
      long_description="TODO",
      keywords='foo bar baz',
      author='Piotr Ożarowski',
      author_email='piotr@debian.org',
      url='http://www.debian.org/',
      license='MIT',
      package_dir={'': 'lib'},
      packages=['foo'],
      package_data = {'foo': ['jquery.js']},
      zip_safe=False,
)
