import unittest
import StringIO
from mock import patch, Mock, MagicMock

from dmtcore.os.disk import linux
from dmtcore.os.disk.base import HctlInfo
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

FAKE_CONTENT_OF_PROC_SCSI = """
Attached devices:
Host: scsi0 Channel: 00 Id: 00 Lun: 00 
  Vendor: TSSTcorp Model: CDDVDW TS-L632H  Rev: TO01
  Type: CD-ROM ANSI  SCSI revision: 05
Host: scsi1 Channel: 00 Id: 02 Lun: 00
  Vendor: IBM Model: 2107900 Rev: .248
  Type: Direct-Access ANSI SCSI revision: 05
Host: scsi1 Channel: 00 Id: 02 Lun: 01
  Vendor: IBM Model: 2107900 Rev: .248
  Type: Direct-Access ANSI SCSI revision: 05
Host: scsi1 Channel: 00 Id: 03 Lun: 00
  Vendor: IBM Model: 2107900 Rev: 5.53
  Type: Direct-Access ANSI SCSI revision: 05
Host: scsi1 Channel: 00 Id: 03 Lun: 01
  Vendor: IBM Model: 2107900 Rev: 5.53
  Type: Direct-Access ANSI SCSI revision: 05
Host: scsi0 Channel: 00 Id: 00 Lun: 00
  Vendor: ATA Model: VBOX HARDDISK Rev: 1.0 
  Type: Direct-Access ANSI SCSI revision: 05
"""

def fake_path_exists(path):
    valid_paths = [
                   "/sys/block/sda/device/scsi_disk:0:0:0:0",
                   "/sys/block/sdb/device/scsi_disk:1:0:2:0",
                   "/sys/block/sdc/device/scsi_disk:1:0:2:1",
                   ]
    return path in valid_paths

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
    
    @patch('os.path.exists', new = fake_path_exists)
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")    
    def test__map_hctl_to_disk_device_name(self, _populate_disks_entries_mock):
        fake_hctl_map = {
                           'sda':HctlInfo(0,0,0,0),
                           'sdb':HctlInfo(1,0,2,0),
                           'sdc':HctlInfo(1,0,2,1),
                           }
        dq = LinuxDiskDeviceQueries()
        #test all possible paths
        #path_exists_mock.assert_called_with("/sys/block/sda/device/scsi_disk:0:0:0:0")
        self.assertEqual(fake_hctl_map, dq._map_hctl_to_disk_device_names(fake_hctl_map.keys()))
    
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")    
    def test__extract_all_hctls_from_proc_scsi_file(self, _populate_disks_entries_mock):
        
        with patch('dmtcore.os.disk.linux.open', create = True) as open_mock:
            open_mock.return_value = MagicMock(spec = file)

            file_handle = open_mock.return_value.__enter__.return_value
            file_handle.readlines.return_value = FAKE_CONTENT_OF_PROC_SCSI.splitlines()
            
            dq = LinuxDiskDeviceQueries()
            expected_results = [
                               HctlInfo(0,0,0,0),
                               HctlInfo(1,0,2,0),
                               HctlInfo(1,0,2,1),
                               HctlInfo(1,0,3,0),
                               HctlInfo(1,0,3,1),
                               HctlInfo(0,0,0,0),
                               ]
            actual_results = dq._extract_all_hctls_from_proc_scsi_file()
            self.assertEqual(len(expected_results), len(actual_results))
            for expected_result, actual_result in map(None, expected_results, actual_results):
                self.assertEqual(expected_result, actual_result)
    
