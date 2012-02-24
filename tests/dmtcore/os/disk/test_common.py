import unittest
from mock import patch

from dmtcore.os.disk.common import get_major_minor

class TestDiskCommon(unittest.TestCase):
    
    @patch('os.stat')
    @patch('os.major')
    @patch('os.minor')
    def test_get_major_minor(self, minor_mock, major_mock, stat_mock):
        major_mock.return_value = 8
        minor_mock.return_value = 0
        result = get_major_minor('/dev/sda')
        major, minor = result
        self.assertTrue(isinstance(result, tuple),"get_major_minor must return a tuple")
        self.assertGreater(major, minor)
