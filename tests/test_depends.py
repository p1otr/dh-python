import os
import unittest
from copy import deepcopy
from pickle import dumps
from tempfile import TemporaryDirectory

from dhpython.depends import Dependencies


class FakeOptions:
    def __init__(self, **kwargs):
        opts = {
            'depends': (),
            'depends_section': (),
            'guess_deps': False,
            'recommends': (),
            'recommends_section': (),
            'requires': (),
            'suggests': (),
            'suggests_section': (),
            'vrange': None,
            'accept_upstream_versions': False,
        }
        opts.update(kwargs)
        for k, v in opts.items():
            setattr(self, k, v)


def prime_pydist(impl, pydist):
    """Fake the pydist data for impl. Returns a cleanup function"""
    from dhpython.pydist import load

    for name, entries in pydist.items():
        if not isinstance(entries, list):
            pydist[name] = entries = [entries]
        for i, entry in enumerate(entries):
            if isinstance(entry, str):
                entries[i] = entry = {'dependency': entry}
            entry.setdefault('name', name)
            entry.setdefault('standard', '')
            entry.setdefault('rules', [])
            entry.setdefault('versions', set())

    key = dumps(((impl,), {}))
    load.cache[key] = pydist
    return lambda: load.cache.pop(key)


class DependenciesTestCase(unittest.TestCase):
    pkg = 'foo'
    impl = 'cpython3'
    pydist = {}
    stats = {
        'compile': False,
        'egg-info': set(),
        'ext_no_version': set(),
        'ext_vers': set(),
        'nsp.txt': set(),
        'private_dirs': {},
        'public_vers': set(),
        'requires.txt': set(),
        'shebangs': set(),
    }
    requires = {}
    options = FakeOptions()

    def setUp(self):
        self.d = Dependencies(self.pkg, self.impl)

        stats = deepcopy(self.stats)
        if self.requires:
            self.tempdir = TemporaryDirectory()
            self.addCleanup(self.tempdir.cleanup)
            old_wd = os.getcwd()
            os.chdir(self.tempdir.name)
            self.addCleanup(os.chdir, old_wd)

            for fn, lines in self.requires.items():
                os.makedirs(os.path.dirname(fn))
                with open(fn, 'w') as f:
                    f.write('\n'.join(lines))
                stats['requires.txt'].add(fn)

        cleanup = prime_pydist(self.impl, self.pydist)
        self.addCleanup(cleanup)

        self.d.parse(stats, self.options)


class TestRequiresCPython3(DependenciesTestCase):
    options = FakeOptions(guess_deps=True)
    pydist = {
        'bar': 'python3-bar',
        'baz': {'dependency': 'python3-baz', 'standard': 'PEP386'},
        'quux': {'dependency': 'python3-quux', 'standard': 'PEP386'},
    }
    requires = {
        'debian/foo/usr/lib/python3/dist-packages/foo.egg-info/requires.txt': (
            'bar',
            'baz >= 1.0',
            'quux',
        ),
    }

    def test_depends_on_bar(self):
        self.assertIn('python3-bar', self.d.depends)

    def test_depends_on_baz(self):
        self.assertIn('python3-baz (>= 1.0)', self.d.depends)


class TestRequiresPyPy(DependenciesTestCase):
    impl = 'pypy'
    options = FakeOptions(guess_deps=True)
    pydist = {
        'bar': 'pypy-bar',
        'baz': {'dependency': 'pypy-baz', 'standard': 'PEP386'},
        'quux': {'dependency': 'pypy-quux', 'standard': 'PEP386'},
    }
    requires = {
        'debian/foo/usr/lib/pypy/dist-packages/foo.egg-info/requires.txt': (
            'bar',
            'baz >= 1.0',
            'quux',
        )
    }

    def test_depends_on_bar(self):
        self.assertIn('pypy-bar', self.d.depends)

    def test_depends_on_baz(self):
        self.assertIn('pypy-baz (>= 1.0)', self.d.depends)
