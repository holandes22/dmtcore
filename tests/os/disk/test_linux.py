import unittest
from mock import patch
from dmtcore.os.disk import linux
from dmtcore.os.disk.linux import LinuxDiskDeviceQueries

FAKE_FDISK_GOOD_OUTPUT = """
Disk /dev/sda: 8185 MB, 8185184256 bytes
255 heads, 63 sectors/track, 995 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes

   Device Boot      Start         End      Blocks   Id  System
/dev/sda1   *           1          13      104391   83  Linux
/dev/sda2              14         995     7887915   8e  Linux LVM
"""

FAKE_FDISK_BAD_OUTPUT = ""

class TestLinuxDiskDeviceQueries(unittest.TestCase):
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__device_name_is_partition__device_is_a_partition(self, _populate_disks_entries_mock):
        dq = LinuxDiskDeviceQueries()
        self.assertEqual(1, _populate_disks_entries_mock.call_count)
        self.assertFalse(dq._device_name_is_partition("sda"))
        self.assertFalse(dq._device_name_is_partition("sdab"))
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__device_name_is_partition__device_is_not_a_partition(self, _populate_disks_entries_mock):
        dq = LinuxDiskDeviceQueries()
        self.assertTrue(dq._device_name_is_partition("sda1"))
        self.assertTrue(dq._device_name_is_partition("sdab12"))
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__device_name_is_partition__device_is_not_valid(self, _populate_disks_entries_mock):
        dq = LinuxDiskDeviceQueries()
        self.assertFalse(dq._device_name_is_partition("/dev/sda1"))
        self.assertFalse(dq._device_name_is_partition("sda1a"))

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_size_from_fdisk_good_output(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_GOOD_OUTPUT
        dq = LinuxDiskDeviceQueries()
        self.assertEqual(8185184256, dq._extract_size_from_fdisk("/dev/sda"))

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_size_from_fdisk_bad_output(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_BAD_OUTPUT
        dq = LinuxDiskDeviceQueries()
        self.assertEqual(None, dq._extract_size_from_fdisk("/dev/sda"))
    
