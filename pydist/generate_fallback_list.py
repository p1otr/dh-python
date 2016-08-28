#! /usr/bin/python3
# Copyright © 2010-2015 Piotr Ożarowski <piotr@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import sys
try:
    from distro_info import DistroInfo  # python3-distro-info package
except ImportError:
    DistroInfo = None
from gzip import decompress
from os import chdir, mkdir
from os.path import dirname, exists, isdir, join, split
from urllib.request import urlopen

if '--ubuntu' in sys.argv and DistroInfo:
    SOURCE = 'http://archive.ubuntu.com/ubuntu/dists/%s/Contents-amd64.gz' % \
             DistroInfo('ubuntu').devel()
else:
    SOURCE = 'http://ftp.debian.org/debian/dists/jessie/main/Contents-amd64.gz'

IGNORED_PKGS = {'python-setuptools', 'python3-setuptools', 'pypy-setuptools'}
DEFAULTS = {
    'cpython2': [
        'python python\n',
        'setuptools python-pkg-resources\n',
        'wsgiref python (>= 2.5) | python-wsgiref\n',
        'argparse python (>= 2.7) | python-argparse\n',
        # not recognized due to .pth file (egg-info is in PIL/ and not in *-packages/)
        'pil python-pil\n',
        'Pillow python-pil\n'],
    'cpython3': [
        'pil python3-pil\n',
        'Pillow python3-pil\n',
        'setuptools python3-pkg-resources\n',
        'argparse python3 (>= 3.2)\n'],
    'pypy': []
}

public_egg = re.compile(r'''
    /usr/
    (
        (?P<cpython2>
            (lib/python2\.[0-9]/((site)|(dist))-packages)|
            (share/python-support/[^/]+)
        )|
        (?P<cpython3>
            (lib/python3/dist-packages)
        )|
        (?P<pypy>
            (lib/pypy/dist-packages)
        )
    )
    /[^/]*\.egg-info
''', re.VERBOSE).match

skip_sensible_names = True if '--skip-sensible-names' in sys.argv else False

chdir(dirname(__file__))
if isdir('../dhpython'):
    sys.path.append('..')
else:
    sys.path.append('/usr/share/dh-python/dhpython/')
from dhpython.pydist import sensible_pname

if not isdir('cache'):
    mkdir('cache')
cache_fpath = join('cache', split(SOURCE)[-1])
if not exists(cache_fpath):
    data = urlopen(SOURCE).read()
    with open(cache_fpath, 'wb') as fp:
        fp.write(data)
else:
    data = open(cache_fpath, 'rb').read()
try:
    data = str(decompress(data), encoding='UTF-8')
except UnicodeDecodeError as e:  # Ubuntu
    data = str(decompress(data), encoding='ISO-8859-15')

result = {
    'cpython2': {},
    'cpython3': {},
    'pypy': {}}

is_header = True
for line in data.splitlines():
    if is_header:
        if line.startswith('FILE'):
            is_header = False
        continue
    try:
        path, desc = line.rsplit(maxsplit=1)
    except ValueError:
        # NOTE(jamespage) some lines in Ubuntu are not parseable.
        continue
    path = '/' + path.rstrip()
    section, pkg_name = desc.rsplit('/', 1)
    if pkg_name in IGNORED_PKGS:
        continue
    match = public_egg(path)
    if match:
        egg_name = [i.split('-', 1)[0] for i in path.split('/')
                    if i.endswith('.egg-info')][0]
        if egg_name.endswith('.egg'):
            egg_name = egg_name[:-4]

        impl = next(key for key, value in match.groupdict().items() if value)

        if skip_sensible_names and\
                sensible_pname(impl, egg_name) == pkg_name:
            continue

        processed = result[impl]
        if egg_name not in processed:
            processed[egg_name] = pkg_name

for impl, details in result.items():
    with open('{}_fallback'.format(impl), 'w') as fp:
        result = DEFAULTS[impl]
        if result:
            fp.writelines(result)
        result = sorted('{} {}\n'.format(egg, pkg) for egg, pkg in details.items())
        fp.writelines(result)
