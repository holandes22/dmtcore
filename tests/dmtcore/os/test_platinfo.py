import unittest
from mock import patch
from dmtcore.os.platinfo import  get_os_name

class Test(unittest.TestCase):

    @patch('platform.system')
    def test_get_os_name_linux(self, system_mock):
        system_mock.return_value = "Linux"
        self.assertEqual("linux", get_os_name())

    @patch('platform.system')
    def test_get_os_name_windows(self, system_mock):
        system_mock.return_value = "Windows"
        self.assertEqual("windows", get_os_name())

    