from tempfile import TemporaryDirectory
import os
import unittest

from dhpython.tools import relpath, move_matching_files


class TestRelpath(unittest.TestCase):
    def test_common_parent_dir(self):
        r = relpath('/usr/share/python-foo/foo.py', '/usr/bin/foo')
        self.assertEqual(r, '../share/python-foo/foo.py')

    def test_strips_common_prefix(self):
        r = relpath('/usr/share/python-foo/foo.py', '/usr/share')
        self.assertEqual(r, 'python-foo/foo.py')

    def test_trailing_slash_ignored(self):
        r = relpath('/usr/share/python-foo/foo.py', '/usr/share/')
        self.assertEqual(r, 'python-foo/foo.py')


class TestMoveMatchingFiles(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        os.makedirs(self.tmppath('foo/bar/a/b/c/spam'))
        for path in ('foo/bar/a/b/c/spam/file.so',
                     'foo/bar/a/b/c/spam/file.py'):
            open(self.tmppath(path), 'w').close()

        move_matching_files(self.tmppath('foo/bar/'),
                            self.tmppath('foo/baz/'),
                            'spam/.*\.so$')

    def tmppath(self, *path):
        return os.path.join(self.tmpdir.name, *path)

    def test_moved_matching_file(self):
        self.assertTrue(os.path.exists(
            self.tmppath('foo/baz/a/b/c/spam/file.so')))

    def test_left_non_matching_file(self):
        self.assertTrue(os.path.exists(
            self.tmppath('foo/bar/a/b/c/spam/file.py')))
