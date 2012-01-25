import unittest
from mock import patch
from dmtcore.os.disk.linux import LinuxDiskDeviceQueries


class TestLinuxDiskDeviceQueries(unittest.TestCase):
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__device_name_is_partition__device_is_a_partition(self, _populate_disks_entries_mock):
        dq = LinuxDiskDeviceQueries()
        self.assertFalse(dq._device_name_is_partition("sda"))
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__device_name_is_partition__device_is_not_a_partition(self, _populate_disks_entries_mock):
        dq = LinuxDiskDeviceQueries()
        self.assertTrue(dq._device_name_is_partition("sda1"))
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__device_name_is_partition__device_is_not_valid(self, _populate_disks_entries_mock):
        dq = LinuxDiskDeviceQueries()
        self.assertFalse(dq._device_name_is_partition("/dev/sda1"))
        self.assertFalse(dq._device_name_is_partition("sda1a"))
