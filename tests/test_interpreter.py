import unittest
from os import environ
from os.path import exists
from dhpython.interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self._triplet = environ.get('DEB_HOST_MULTIARCH')
        environ['DEB_HOST_MULTIARCH'] = 'MYARCH'

    def tearDown(self):
        if self._triplet:
            environ['DEB_HOST_MULTIARCH'] = self._triplet

    @unittest.skipUnless(exists('/usr/bin/pypy'), 'pypy is not installed')
    def test_pypy(self):
        sorted(Interpreter.parse('pypy').items()) == \
            [('debug', None), ('name', 'pypy'), ('options', ()), ('path', ''), ('version', None)]
        sorted(Interpreter.parse('#! /usr/bin/pypy --foo').items()) == \
            [('debug', None), ('name', 'pypy'), ('options', ('--foo',)), ('path', '/usr/bin/'), ('version', None)]
        Interpreter('pypy').sitedir(version='2.0') == '/usr/lib/pypy/dist-packages/'

    @unittest.skipUnless(exists('/usr/bin/python2.6'), 'python2.6 is not installed')
    def test_python26(self):
        i = Interpreter('python2.6')
        self.assertEqual(i.soabi(), '')
        self.assertIsNone(i.check_extname('foo.so'))
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertIsNone(i.check_extname('foo/bar/bazmodule.so'))

    @unittest.skipUnless(exists('/usr/bin/python2.6-dbg'), 'python2.6-dbg is not installed')
    def test_python26dbg(self):
        i = Interpreter('python2.6-dbg')
        self.assertEqual(i.soabi(), '')
        self.assertIsNone(i.check_extname('foo_d.so'))
        self.assertEqual(i.check_extname('foo.so'), 'foo_d.so')
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), 'foo/bar/bazmodule_d.so')

    @unittest.skipUnless(exists('/usr/bin/python2.7'), 'python2.7 is not installed')
    def test_python27(self):
        i = Interpreter('python2.7')
        self.assertEqual(i.soabi(), '')
        self.assertEqual(i.check_extname('foo.so'), 'foo.MYARCH.so')
        self.assertIsNone(i.check_extname('foo.MYARCH_d.so'))
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertIsNone(i.check_extname('foo.OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), 'foo/bar/baz.MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python2.7-dbg'), 'python2.7-dbg is not installed')
    def test_python27dbg(self):
        i = Interpreter('python2.7-dbg')
        self.assertEqual(i.soabi(), '')
        self.assertEqual(i.check_extname('foo.so'), 'foo.MYARCH_d.so')
        self.assertEqual(i.check_extname('foo_d.so'), 'foo.MYARCH_d.so')
        self.assertIsNone(i.check_extname('foo.MYARCH_d.so'))
        self.assertIsNone(i.check_extname('foo.OTHER_d.so'))  # different architecture
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), 'foo/bar/baz.MYARCH_d.so')

    @unittest.skipUnless(exists('/usr/bin/python3.1'), 'python3.1 is not installed')
    def test_python31(self):
        i = Interpreter('python3.1')
        self.assertEqual(i.soabi(), '')
        self.assertIsNone(i.check_extname('foo.so'))
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertIsNone(i.check_extname('foo/bar/bazmodule.so'))

    @unittest.skipUnless(exists('/usr/bin/python3.1-dbg'), 'python3.1-dbg is not installed')
    def test_python31dbg(self):
        i = Interpreter('python3.1-dbg')
        self.assertEqual(i.soabi(), '')
        self.assertIsNone(i.check_extname('foo.so'))
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertIsNone(i.check_extname('foo/bar/bazmodule.so'))

    @unittest.skipUnless(exists('/usr/bin/python3.2'), 'python3.2 is not installed')
    def test_python32(self):
        i = Interpreter('python3.2')
        self.assertEqual(i.soabi(), 'cpython-32mu')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-32mu.so')
        self.assertIsNone(i.check_extname('foo.cpython-33m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-32mu-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/bazmodule.cpython-32mu.so')

    @unittest.skipUnless(exists('/usr/bin/python3.2-dbg'), 'python3.2-dbg is not installed')
    def test_python32dbg(self):
        i = Interpreter('python3.2-dbg')
        self.assertEqual(i.soabi(), 'cpython-32dmu')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-32dmu.so')
        self.assertIsNone(i.check_extname('foo.cpython-33m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-32dmu-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/bazmodule.cpython-32dmu.so')

    @unittest.skipUnless(exists('/usr/bin/python3.4'), 'python3.4 is not installed')
    def test_python34(self):
        i = Interpreter('python3.4')
        self.assertEqual(i.soabi(), 'cpython-34m')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-34m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-34m-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-34m.so'), r'foo.cpython-34m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-34m-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.4-dbg'), 'python3.4-dbg is not installed')
    def test_python34dbg(self):
        i = Interpreter('python3.4-dbg')
        self.assertEqual(i.soabi(), 'cpython-34dm')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-34dm-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-34m-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-34dm-MYARCH.so')

    def test_version(self):
        i = Interpreter(impl='cpython2')
        self.assertEqual(str(i), 'python')
        self.assertEqual(i.binary('2.7'), '/usr/bin/python2.7')

if __name__ == '__main__':
    unittest.main()
