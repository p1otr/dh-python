from unittest import TestCase


class RequiredTest(TestCase):
    def test_tests_are_executed(self):
        open('test-executed', 'w').close()
