# Copyright © 2013 Piotr Ożarowski <piotr@debian.org>
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

import logging
from filecmp import cmp as cmpfile
from os import listdir, remove, renames, rmdir
from os.path import exists, isdir, join

log = logging.getLogger(__name__)


def fix_locations(package, interpreter, versions):
    """Move files to the right location."""
    for version in versions:
        interpreter.version = version

        dstdir = interpreter.sitedir(package)
        for srcdir in interpreter.old_sitedirs(package):
            if isdir(srcdir):
                # TODO: what about relative symlinks?
                log.debug('moving files from %s to %s', srcdir, dstdir)
                share_files(srcdir, dstdir, interpreter)
                parent_dir = '/'.join(srcdir.split('/')[:-1])
                if exists(parent_dir) and not listdir(parent_dir):
                    rmdir(parent_dir)

        # do the same with debug locations
        dstdir = interpreter.sitedir(package, gdb=True)
        for srcdir in interpreter.old_sitedirs(package, gdb=True):
            if isdir(srcdir):
                log.debug('moving files from %s to %s', srcdir, dstdir)
                share_files(srcdir, dstdir, interpreter)
                parent_dir = '/'.join(srcdir.split('/')[:-1])
                if exists(parent_dir) and not listdir(parent_dir):
                    rmdir(parent_dir)


def share_files(srcdir, dstdir, interpreter):
    """Try to move as many files from srcdir to dstdir as possible."""
    for i in listdir(srcdir):
        fpath1 = join(srcdir, i)
        if i.rsplit('.', 1)[-1] == 'so':
            # try to rename extension here as well (in :meth:`scan` info about
            # Python version is gone)
            version = interpreter.parse_public_version(srcdir)
            if version:
                # note that if ver is empty, default Python version will be used
                fpath1_orig = fpath1
                new_name = interpreter.check_extname(i, version)
                if new_name:
                    fpath1 = join(srcdir, new_name)
                if exists(fpath1):
                    log.warn('destination file exist, '
                             'cannot rename %s to %s', fpath1_orig, fpath1)
                else:
                    log.warn('renaming %s to %s', fpath1_orig, fpath1)
                    renames(fpath1_orig, fpath1)
        fpath2 = join(dstdir, i)
        if not exists(fpath2):
            renames(fpath1, fpath2)
            continue
        if isdir(fpath1):
            share_files(fpath1, fpath2, interpreter)
        elif cmpfile(fpath1, fpath2, shallow=False):
            remove(fpath1)
        # XXX: check symlinks

    if exists(srcdir) and not listdir(srcdir):
        rmdir(srcdir)


