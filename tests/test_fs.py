from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import TestCase

from dhpython.fs import (
    fix_merged_RECORD, merge_RECORD, merge_WHEEL, missing_lines)


class MergeWheelTestCase(TestCase):
    files = {}
    def setUp(self):
        self.tempdir = TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        temp_path = Path(self.tempdir.name)
        for fn, contents in self.files.items():
            path = temp_path / fn
            setattr(self, path.name, path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w') as f:
                f.write('\n'.join(contents))
                f.write('\n')

    def assertFileContents(self, path, contents):
        """Assert that the contents of path is contents

        Contents may be specified as a list of strings, one per line, without
        line-breaks.
        """
        if isinstance(contents, (list, tuple)):
            contents = '\n'.join(contents) + '\n'
        with path.open('r') as f:
            self.assertMultiLineEqual(contents, f.read())


class SimpleCombinationTestCase(MergeWheelTestCase):
    files = {
        'a': ('abc', 'def'),
        'b': ('abc', 'ghi'),
    }
    def test_missing_lines(self):
        r = missing_lines(self.a, self.b)
        self.assertEqual(r, ['def\n'])

    def test_merge_record(self):
        merge_RECORD(self.a, self.b)
        self.assertFileContents(self.b, ('abc', 'ghi', 'def'))


class MergeTagsTestCase(MergeWheelTestCase):
    files = {
        'a': ('foo', 'Tag: A'),
        'b': ('foo', 'Tag: B'),
    }

    def test_merge_wheel(self):
        merge_WHEEL(self.a, self.b)
        self.assertFileContents(self.b, ('foo', 'Tag: B', 'Tag: A'))


class UpdateRecordTestCase(MergeWheelTestCase):
    files = {
        'dist-info/RECORD': ('dist-info/FOO,sha256=b5bb9d8014a0f9b1d61e21e796d7'
                             '8dccdf1352f23cd32812f4850b878ae4944c,4',),
        'dist-info/WHEEL': ('foo'),
    }

    def test_fix_merged_record(self):
        fix_merged_RECORD(self.RECORD.parent)
        self.assertFileContents(self.RECORD, (
            'dist-info/FOO,sha256=b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32'
            '812f4850b878ae4944c,4',
            'dist-info/WHEEL,sha256=447fb61fa39a067229e1cce8fc0953bfced53eac85d'
            '1844f5940f51c1fcba725,6',
        ))
