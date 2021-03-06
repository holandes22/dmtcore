import unittest
from mock import patch, MagicMock

from dmtcore.os.disk import linux
from dmtcore.os.disk.base import HctlInfo, DiskEntry
from dmtcore.os.disk.linux import LinuxDiskDeviceQueries, LinuxDeviceMapper,\
    LinuxPathEntry, LinuxPathGroupEntry
from dmtcore.os.commands import SIZE_FROM_FDISK


FAKE_FDISK_GOOD_OUTPUT = """
Disk /dev/sda: 8185 MB, 8185184256 bytes
255 heads, 63 sectors/track, 995 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x0001ab30

   Device Boot      Start         End      Blocks   Id  System
/dev/sda1   *           1          13      104391   83  Linux
/dev/sda2              14         995     7887915   8e  Linux LVM
"""

FAKE_FDISK_GOOD_OUTPUT_PARTITION = """
Disk /dev/sda6: 126.0 GB, 125998989312 bytes
255 heads, 63 sectors/track, 15318 cylinders, total 246091776 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x00000000

Disk /dev/sda6 doesn't contain a valid partition table
"""

FAKE_FDISK_GOOD_OUTPUT_MULTIPATH_DEVICE = """
Disk /dev/mapper/mpatha doesn't contain a valid partition table

Disk /dev/mapper/mpathc: 17.2 GB, 17208180736 bytes
255 heads, 63 sectors/track, 2092 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x00000000

Disk /dev/mapper/mpathc doesn't contain a valid partition table

Disk /dev/mapper/mpathb: 17.2 GB, 17208180736 bytes
255 heads, 63 sectors/track, 2092 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x00000000

Disk /dev/mapper/mpathb doesn't contain a valid partition table
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

FAKE_BLKID_OUTPUT = """
UUID=51270839-1a9b-44a2-9786-e078206342c2
TYPE=ext4
"""

FAKE_MULTIPATH_LIST_RHEL5_OUTPUT = """
mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
[size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
\_ round-robin 0 [prio=6][active]
 \_ 29:0:0:1 sdf 8:80  [active][ready]
 \_ 28:0:1:1 sdl 8:176 [active][ready]
\_ round-robin 0 [prio=0][enabled]
 \_ 28:0:0:1 sdb 8:16  [active][ghost]
 \_ 29:0:1:1 sdq 65:0  [active][ghost]
mpatha (200173800fe0000aa) dm-2 IBM,1815      FAStT
[size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
\_ round-robin 0 [prio=1][enabled]
 \_ 33:0:0:1 sda 8:94  [active][ready]
 \_ 34:0:2:1 sdb 8:233 [active][ready]
"""

FAKE_MULTIPATH_LIST_RHEL5_SINGLE_DEVICE_SEVERAL_PATH_GROUPS_OUTPUT = """
mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
[size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
\_ round-robin 0 [prio=6][active]
 \_ 29:0:0:1 sdf 8:80  [active][ready]
 \_ 28:0:1:1 sdl 8:176 [active][ready]
\_ round-robin 0 [prio=1][enabled]
 \_ 28:0:0:1 sdb 8:16  [active][ghost]
 \_ 29:0:1:1 sdq 65:0  [active][ghost]
"""

FAKE_MULTIPATH_LIST_RHEL5_SINGLE_DEVICE_ONE_PATH_GROUP_OUTPUT = """
mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
[size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
\_ round-robin 0 [prio=6][active]
 \_ 29:0:0:1 sdf 8:80  [active][ready]
 \_ 28:0:1:1 sdl 8:176 [active][ghost]
"""

FAKE_MULTIPATH_LIST_RHEL6_SINGLE_DEVICE_SEVERAL_PATH_GROUPS_OUTPUT = """
Mar 23 09:20:47 | /lib/udev/scsi_id exitted with 1
mpathc (200173800fe0000aa) dm-4 IBM,2810XIV
size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='round-robin 0' prio=1 status=active
  |- 3:0:0:2  sdc 8:32 active faulty running
  `- 4:0:0:2  sde 8:64 active ready running
`-+- policy='round-robin 0' prio=1 status=active
  |- 5:0:0:2  sdf 8:33 active shaky running
  `- 6:0:0:2  sdg 8:65 active ready running
"""

FAKE_MULTIPATH_LIST_RHEL6_SINGLE_DEVICE_ONE_PATH_GROUP_OUTPUT = """
mpathc (200173800fe0000aa) dm-4 IBM,2810XIV
size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='round-robin 0' prio=1 status=active
  |- 3:0:0:2  sdc 8:32 active faulty running
  `- 4:0:0:2  sde 8:64 active ready running
"""

FAKE_MULTIPATH_LIST_RHEL6_OUTPUT = """
mpathc (200173800fe0000aa) dm-4 IBM,2810XIV
size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='round-robin 0' prio=1 status=active
  |- 3:0:0:2  sdc 8:32 active faulty running
  `- 4:0:0:2  sde 8:64 active ready running
mpatha (200173800fdfd12b8) dm-2 IBM,2810XIV
size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='round-robin 0' prio=1 status=active
  `- 5:0:0:77 sdf 8:80 active ready running
pablodev (200173800fe0000a9) dm-3 IBM,2810XIV
size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='round-robin 0' prio=1 status=active
  |- 4:0:0:1  sdd 8:48 active shaky running
  `- 3:0:0:1  sdb 8:16 active ready running
"""


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

    @patch("dmtcore.os.disk.linux.run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_size_from_fdisk_good_output(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_GOOD_OUTPUT
        dq = LinuxDiskDeviceQueries()
        fake_device_filepath = "/dev/sda"
        actual_size = dq._extract_size_from_fdisk(fake_device_filepath)
        run_cmd_mock.assert_called_with(SIZE_FROM_FDISK + [fake_device_filepath])
        self.assertEqual(8185184256, actual_size)

    @patch("dmtcore.os.disk.linux.run_cmd")
    def test_get_disk_identifier(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_GOOD_OUTPUT
        dq = LinuxDiskDeviceQueries()
        fake_device_filepath = "/dev/sdb"
        actual_identifier = dq.get_disk_identifier(fake_device_filepath)
        run_cmd_mock.assert_called_with(SIZE_FROM_FDISK + [fake_device_filepath])
        self.assertEqual("0x0001ab30", actual_identifier)

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_size_from_fdisk_good_output_multipath_device(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_GOOD_OUTPUT_MULTIPATH_DEVICE
        dq = LinuxDiskDeviceQueries()
        fake_device_filepath = "/dev/mapper/mpathc"
        actual_size = dq._extract_size_from_fdisk(fake_device_filepath)
        run_cmd_mock.assert_called_once_with(SIZE_FROM_FDISK + [fake_device_filepath])
        self.assertEqual(17208180736, actual_size)

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_size_from_fdisk_good_output_partition(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_GOOD_OUTPUT_PARTITION
        dq = LinuxDiskDeviceQueries()
        fake_device_filepath = "/dev/sda6"
        actual_size = dq._extract_size_from_fdisk(fake_device_filepath)
        run_cmd_mock.assert_called_once_with(SIZE_FROM_FDISK + [fake_device_filepath])
        self.assertEqual(125998989312, actual_size)

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_size_from_fdisk_bad_output(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_FDISK_BAD_OUTPUT
        dq = LinuxDiskDeviceQueries()
        self.assertEqual(None, dq._extract_size_from_fdisk("/dev/sda"))

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

    @patch.object(linux, 'get_major_minor', new = lambda x: (250, int(x[-1])))
    @patch.object(linux, 'glob')
    @patch.object(LinuxDiskDeviceQueries, "_extract_size_from_fdisk")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__get_sysfs_partitions(self, _populate_disks_entries_mock, extract_size_mock, glob_mock):
        glob_mock.return_value = ['/dev/sda1', '/dev/sda2', '/dev/sda3']
        fake_size = 1024
        extract_size_mock.return_value = fake_size
        dq = LinuxDiskDeviceQueries()
        expected_results = [
                            DiskEntry('sda1', '/dev/sda1', fake_size, (250, 1), (1,1,1,1)),
                            DiskEntry('sda2', '/dev/sda2', fake_size, (250, 2), (2,2,2,2)),
                            DiskEntry('sda3', '/dev/sda3', fake_size, (250, 3), (3,3,3,3)),
                            ]
        # TODO: This is kinda ugly, better would be to mock _map_hctl_to_disk_device_names
        dq.hctl_map = {
                       "sda1": (1,1,1,1),
                       "sda2": (2,2,2,2),
                       "sda3": (3,3,3,3),
                       }
        actual_results = dq._get_sysfs_partitions('sda')
        self.assertEqual(len(expected_results), len(actual_results))
        for expected_result, actual_result in map(None, expected_results, actual_results):
            self.assertEqual(expected_result.name, actual_result.name)
            self.assertEqual(expected_result.filepath, actual_result.filepath)
            self.assertEqual(expected_result.size, actual_result.size)
            self.assertEqual(expected_result.major_minor, actual_result.major_minor)
            self.assertEqual(expected_result.hctl, actual_result.hctl)

    @patch('os.readlink')
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_hctl_from_device_link(self, _populate_disks_entries_mock, readlink_mock):
        def readlink_side_effect(device_name):
            links = {
                     "/sys/block/sda/device": "../../../0:0:0:0",
                     "/sys/block/sdb/device": "0000:00/0000:00:10:0/host0/target0:0:0/0:0:0:0",
                     "/sys/block/sdc/device": "platform/host1/session1/target1:0:0:1/1:0:0:3",
                     "/sys/block/sdd/device": "../../../15:16:17:333",
                     }
            return links[device_name]
        device_names = [
                 "sda",
                 "sdb",
                 "sdc",
                 "sdd",
                 ]
        expected_results = [
                            HctlInfo(0,0,0,0),
                            HctlInfo(0,0,0,0),
                            HctlInfo(1,0,0,3),
                            HctlInfo(15,16,17,333),
                            ]

        readlink_mock.side_effect = readlink_side_effect
        dq = LinuxDiskDeviceQueries()
        for expected_result, device_name in map(None, expected_results, device_names):
            self.assertEqual(expected_result, dq._extract_hctl_from_device_link(device_name))

    @patch('os.readlink')
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_hctl_from_device_link_returns_none_on_oserror(
                                                                    self,
                                                                    _populate_disks_entries_mock,
                                                                    readlink_mock
                                                                    ):
        readlink_mock.side_effect = OSError()
        dq = LinuxDiskDeviceQueries()
        self.assertEqual(None, dq._extract_hctl_from_device_link("sda"))

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_uuid_from_blkid(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_BLKID_OUTPUT
        fake_device_filepath = "/dev/sda1"
        dq = LinuxDiskDeviceQueries()
        self.assertEqual("51270839-1a9b-44a2-9786-e078206342c2",
                         dq._extract_uuid_from_blkid(fake_device_filepath))

    @patch.object(linux, "run_cmd")
    @patch.object(LinuxDiskDeviceQueries, "_populate_disks_entries")
    def test__extract_uuid_from_blkid_no_uuid(self, _populate_disks_entries_mock, run_cmd_mock):
        run_cmd_mock.return_value = ""
        fake_device_filepath = "/dev/sda1"
        dq = LinuxDiskDeviceQueries()
        self.assertEqual(None, dq._extract_uuid_from_blkid(fake_device_filepath))


class TestLinuxDeviceMapper(unittest.TestCase):

    @patch.object(linux, "run_cmd")
    def test_get_multipath_disks_details_rhel6(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_MULTIPATH_LIST_RHEL6_OUTPUT
        ldm = LinuxDeviceMapper()
        expected_results = {
                            "mpathc": ("200173800fe0000aa", "IBM,2810XIV", "dm-4", "mpathc"),
                            "mpatha": ("200173800fdfd12b8", "IBM,2810XIV", "dm-2", "mpatha"),
                            "pablodev": ("200173800fe0000a9", "IBM,2810XIV", "dm-3", "pablodev"),
                            }
        self.assertEqual(expected_results, ldm.get_multipath_disks_details())

    @patch.object(linux, "run_cmd")
    def test_get_multipath_disks_details_rhel5(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_MULTIPATH_LIST_RHEL5_OUTPUT
        ldm = LinuxDeviceMapper()
        expected_results = {
                            "mydev1": ("3600a0b800011a1ee0000040646828cc5", "IBM,1815", "dm-1", "mydev1"),
                            "mpatha": ("200173800fe0000aa", "IBM,1815", "dm-2", "mpatha"),
                            }
        self.assertEqual(expected_results, ldm.get_multipath_disks_details())

    @patch.object(LinuxDeviceMapper, "_extract_relevant_device_lines_from_multipath")
    def test__extract_path_groups_details_rhel5_several_path_groups(self, extract_lines):
        extract_lines.return_value = """
        mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
        [size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
        \_ round-robin 0 [prio=6][active]
        \_ 29:0:0:1 sdf 8:80  [active][ready]
        \_ 28:0:1:1 sdl 8:176 [active][ready]
        \_ round-robin 0 [prio=1][enabled]
        \_ 28:0:0:1 sdb 8:16  [active][ghost]
        \_ 29:0:1:1 sdq 65:0  [active][ghost]
       """.strip().splitlines()
        ldm = LinuxDeviceMapper()
        expected_results = [
                            LinuxPathGroupEntry("active", 6, "round-robin", 0, [
                                                             LinuxPathEntry("ready", "active", "sdf"),
                                                             LinuxPathEntry("ready", "active", "sdl"),
                                                            ]
                            ),
                            LinuxPathGroupEntry("enabled", 1, "round-robin", 0, [
                                                              LinuxPathEntry("ghost", "active", "sdb"),
                                                              LinuxPathEntry("ghost", "active", "sdq"),
                                                             ]
                             ),
                            ]

        self.assertEqual(expected_results,
                         ldm._extract_path_groups_details("fake_device"))

    @patch.object(LinuxDeviceMapper, "_extract_relevant_device_lines_from_multipath")
    def test__extract_path_groups_details_rhel5_one_path_group(self, extract_lines):
        extract_lines.return_value = """
        mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
        [size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
        \_ round-robin 0 [prio=6][active]
        \_ 29:0:0:1 sdf 8:80  [active][ready]
        \_ 28:0:1:1 sdl 8:176 [active][ghost]
        """.strip().splitlines()
        ldm = LinuxDeviceMapper()
        expected_results = [
                            LinuxPathGroupEntry("active", 6, "round-robin", 0, [
                                                             LinuxPathEntry("ready", "active", "sdf"),
                                                             LinuxPathEntry("ghost", "active", "sdl"),
                                                            ]
                            )
                            ]

        self.assertEqual(expected_results,
                         ldm._extract_path_groups_details("fake_device"))

    @patch.object(LinuxDeviceMapper, "_extract_relevant_device_lines_from_multipath")
    def test__extract_path_groups_details_rhel6_several_path_groups(self, extract_lines):
        extract_lines.return_value = """
        mpathc (200173800fe0000aa) dm-4 IBM,2810XIV
        size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
        `-+- policy='round-robin 0' prio=1 status=active
        |- 3:0:0:2  sdc 8:32 active faulty running
        `- 4:0:0:2  sde 8:64 active ready running
        `-+- policy='round-robin 0' prio=1 status=active
        |- 5:0:0:2  sdf 8:33 active shaky running
        `- 6:0:0:2  sdg 8:65 active ready running
        """.strip().splitlines()
        ldm = LinuxDeviceMapper()
        expected_results = [
                            LinuxPathGroupEntry("active", 1, "round-robin", 0, [
                                                             LinuxPathEntry("faulty", "active", "sdc"),
                                                             LinuxPathEntry("ready", "active", "sde"),
                                                            ]
                            ),
                            LinuxPathGroupEntry("active", 1, "round-robin", 0, [
                                                              LinuxPathEntry("shaky", "active", "sdf"),
                                                              LinuxPathEntry("ready", "active", "sdg"),
                                                             ]
                             ),
                            ]

        self.assertEqual(expected_results,
                         ldm._extract_path_groups_details("fake_device"))

    @patch.object(LinuxDeviceMapper, "_extract_relevant_device_lines_from_multipath")
    def test__extract_path_groups_details_rhel6_one_path_group(self, extract_lines):
        extract_lines.return_value = """
        mpathc (200173800fe0000aa) dm-4 IBM,2810XIV
        size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
        `-+- policy='round-robin 0' prio=1 status=active
        |- 3:0:0:2  sdc 8:32 active faulty running
        `- 4:0:0:2  sde 8:64 active ready running
        """.strip().splitlines()
        ldm = LinuxDeviceMapper()
        expected_results = [
                            LinuxPathGroupEntry("active", 1, "round-robin", 0, [
                                                             LinuxPathEntry("faulty", "active", "sdc"),
                                                             LinuxPathEntry("ready", "active", "sde"),
                                                            ]
                            )
                            ]

        self.assertEqual(expected_results,
                         ldm._extract_path_groups_details("fake_device"))

    def test__extract_paths_details_rhel5(self):
        ldm = LinuxDeviceMapper()
        expected_results = LinuxPathEntry("ready", "active", "sdf")
        self.assertEqual(expected_results, ldm._extract_paths_details(" \_ 29:0:0:1 sdf 8:80  [active][ready]"))

    def test__extract_paths_details_rhel6(self):
        ldm = LinuxDeviceMapper()
        expected_results = LinuxPathEntry("faulty", "active", "sdc")
        self.assertEqual(expected_results, ldm._extract_paths_details("  |- 3:0:0:2  sdc 8:32 active faulty running"))

    @patch.object(linux, "run_cmd")
    def test__extract_relevant_device_lines_from_multipath_multiple_devices_rhel5(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_MULTIPATH_LIST_RHEL5_OUTPUT
        ldm = LinuxDeviceMapper()
        expected_result = """
        mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
        [size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
        \_ round-robin 0 [prio=6][active]
         \_ 29:0:0:1 sdf 8:80  [active][ready]
         \_ 28:0:1:1 sdl 8:176 [active][ready]
        \_ round-robin 0 [prio=0][enabled]
         \_ 28:0:0:1 sdb 8:16  [active][ghost]
         \_ 29:0:1:1 sdq 65:0  [active][ghost]
        """.strip().splitlines()
        self.assertEqual([l.strip() for l in expected_result], ldm._extract_relevant_device_lines_from_multipath("mydev1"))

    @patch.object(linux, "run_cmd")
    def test__extract_relevant_device_lines_from_multipath_single_device_rhel5(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_MULTIPATH_LIST_RHEL5_SINGLE_DEVICE_SEVERAL_PATH_GROUPS_OUTPUT
        ldm = LinuxDeviceMapper()
        expected_result = """mydev1 (3600a0b800011a1ee0000040646828cc5) dm-1 IBM,1815      FAStT
        [size=512M][features=1 queue_if_no_path][hwhandler=1 rdac]
        \_ round-robin 0 [prio=6][active]
         \_ 29:0:0:1 sdf 8:80  [active][ready]
         \_ 28:0:1:1 sdl 8:176 [active][ready]
        \_ round-robin 0 [prio=1][enabled]
         \_ 28:0:0:1 sdb 8:16  [active][ghost]
         \_ 29:0:1:1 sdq 65:0  [active][ghost]
        """.strip().splitlines()
        self.assertEqual([l.strip() for l in expected_result], ldm._extract_relevant_device_lines_from_multipath("mydev1"))

    @patch.object(linux, "run_cmd")
    def test__extract_relevant_device_lines_from_multipath_multiple_devices_rhel6(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_MULTIPATH_LIST_RHEL6_OUTPUT
        ldm = LinuxDeviceMapper()
        expected_result = """
        mpatha (200173800fdfd12b8) dm-2 IBM,2810XIV
        size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
        `-+- policy='round-robin 0' prio=1 status=active
            `- 5:0:0:77 sdf 8:80 active ready running
        """.strip().splitlines()
        self.assertEqual([l.strip() for l in expected_result], ldm._extract_relevant_device_lines_from_multipath("mpatha"))

    @patch.object(linux, "run_cmd")
    def test__extract_relevant_device_lines_from_multipath_single_device_rhel6(self, run_cmd_mock):
        run_cmd_mock.return_value = FAKE_MULTIPATH_LIST_RHEL6_SINGLE_DEVICE_SEVERAL_PATH_GROUPS_OUTPUT
        ldm = LinuxDeviceMapper()
        expected_result = """
        mpathc (200173800fe0000aa) dm-4 IBM,2810XIV
        size=16G features='1 queue_if_no_path' hwhandler='0' wp=rw
        `-+- policy='round-robin 0' prio=1 status=active
            |- 3:0:0:2  sdc 8:32 active faulty running
            `- 4:0:0:2  sde 8:64 active ready running
        `-+- policy='round-robin 0' prio=1 status=active
            |- 5:0:0:2  sdf 8:33 active shaky running
            `- 6:0:0:2  sdg 8:65 active ready running
        """.strip().splitlines()
        self.assertEqual([l.strip() for l in expected_result], ldm._extract_relevant_device_lines_from_multipath("mpathc"))
