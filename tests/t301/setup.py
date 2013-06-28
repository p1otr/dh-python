#! /usr/bin/python3
from distutils.core import setup

setup(name='Foo',
      version='0.2',
      description="package with public modules only",
      long_description="TODO",
      keywords='foo bar baz',
      author='Piotr Ożarowski',
      author_email='piotr@debian.org',
      url='http://www.debian.org/',
      license='MIT',
      packages=['foo'],
      package_dir={'foo': 'lib/foo'},
      package_data={'foo': ['jquery.js']},
      zip_safe=False,
      install_requires=['Mako', 'Baz [extras]'])
