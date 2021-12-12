from tempfile import TemporaryDirectory
import unittest
import os

from dhpython.debhelper import DebHelper, build_options


class DebHelperTestCase(unittest.TestCase):
    impl = 'cpython3'
    control = []
    options = {}
    parse_control = True

    def build_options(self):
        return build_options(**self.options)

    def setUp(self):
        self.tempdir = TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

        old_wd = os.getcwd()
        os.chdir(self.tempdir.name)
        self.addCleanup(os.chdir, old_wd)

        os.mkdir('debian')
        with open('debian/control', 'w') as f:
            f.write('\n'.join(self.control))
        if self.parse_control:
            self.dh = DebHelper(self.build_options(), impl=self.impl)


CONTROL = [
    'Source: foo-src',
    'Build-Depends: python3-all,',
    ' python-all,',
    ' bar (<< 2) [amd64],',
    ' baz (>= 1.0)',
    'X-Python3-Version: >= 3.1, << 3.10',
    '',
    'Architecture: all',
    'Package: python3-foo',
    'Depends: ${python3:Depends}',
    '',
    'Package: python3-foo-ext',
    'Architecture: any',
    'Depends: ${python3:Depends}, '
    '# COMMENT',
    ' ${shlibs:Depends},',
    '',
    'Package: python-foo',
    'Architecture: all',
    'Depends: ${python:Depends}',
    '',
    '',
    'Package: foo',
    'Architecture: all',
    'Depends: ${python3:Depends}',
    '',
    '',
]

class TestControlBlockParsing(DebHelperTestCase):
    control = CONTROL

    def test_parses_source(self):
        self.assertEqual(self.dh.source_name, 'foo-src')

    def test_parses_build_depends(self):
        self.assertEqual(self.dh.build_depends, {
            'python3-all': {None: None},
            'python-all': {None: None},
            'bar': {'amd64': '<< 2'},
            'baz': {None: '>= 1.0'},
        })

    def test_parses_XPV(self):
        self.assertEqual(self.dh.python_version, '>= 3.1, << 3.10')

    def test_parses_packages(self):
        self.assertEqual(list(self.dh.packages.keys()),
                         ['python3-foo', 'python3-foo-ext', 'foo'])

    def test_parses_arch(self):
        self.assertEqual(self.dh.packages['python3-foo-ext']['arch'], 'any')

    def test_parses_arch_all(self):
        self.assertEqual(self.dh.packages['python3-foo']['arch'], 'all')


class TestControlSkipIndep(DebHelperTestCase):
    control = CONTROL
    options = {
        'arch': True,
    }

    def test_skip_indep(self):
        self.assertEqual(list(self.dh.packages.keys()), ['python3-foo-ext'])


class TestControlSkipArch(DebHelperTestCase):
    control = CONTROL
    options = {
        'arch': False,
    }

    def test_skip_arch(self):
        self.assertEqual(list(self.dh.packages.keys()), ['python3-foo', 'foo'])


class TestControlSinglePkg(DebHelperTestCase):
    control = CONTROL
    options = {
        'package': ['python3-foo'],
    }

    def test_parses_packages(self):
        self.assertEqual(list(self.dh.packages.keys()), ['python3-foo'])


class TestControlSkipSinglePkg(DebHelperTestCase):
    control = CONTROL
    options = {
        'no_package': ['python3-foo'],
    }

    def test_parses_packages(self):
        self.assertEqual(list(self.dh.packages.keys()),
                         ['python3-foo-ext', 'foo'])


class TestControlBlockParsingPy2(DebHelperTestCase):
    control = CONTROL
    impl = 'cpython2'

    def test_parses_packages(self):
        self.assertEqual(list(self.dh.packages.keys()), ['python-foo'])


class TestControlNoBinaryPackages(DebHelperTestCase):
    control = [
        'Source: foo-src',
        'Build-Depends: python3-all',
        '',
    ]
    parse_control = False

    def test_throws_error(self):
        msg = ('Unable to parse debian/control, found less than 2 paragraphs')
        with self.assertRaisesRegex(Exception, msg):
            DebHelper(self.build_options())


class TestControlMissingPackage(DebHelperTestCase):
    control = [
        'Source: foo-src',
        'Build-Depends: python3-all',
        '',
        'Architecture: all',
    ]
    parse_control = False

    def test_parses_packages(self):
        msg = ('Unable to parse debian/control, paragraph 2 missing Package '
               'field')
        with self.assertRaisesRegex(Exception, msg):
            DebHelper(self.build_options())
