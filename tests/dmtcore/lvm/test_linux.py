import unittest
from mock import patch
from dmtcore.lvm.api import PhysicalVolume, VolumeGroup, LogicalVolume
from dmtcore.lvm.linux import VolumeManager

ALL_PVS_OUTPUT = """
   Scanning for physical volume names
    PV|VG|Fmt|Attr|PSize|PFree|DevSize|PV UUID
    /dev/sdd1|data|lvm2|a-|488.00m|72.00m|488.28m|Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll
    /dev/sdd2|data|lvm2|a-|532.00m|532.00m|534.72m|5b25y8-bRvk-m5Nb-rsRK-Wjqf-W34E-Hhpouo
    /dev/sde1|vg1|lvm2|a-|200.00m|240.00m|241.75m|sde1
    /dev/sde2||lvm2|a-|200.00m|292.97m|292.97m|sde2
    /dev/sde3||lvm2|a-|200.00m|488.28m|488.28m|sde3
"""

ONE_PVS_OUTPUT = """
   Scanning for physical volume names
    PV|VG|Fmt|Attr|PSize|PFree|DevSize|PV UUID
    /dev/sdd1|data|lvm2|a-|488.00m|72.00m|488.28m|Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll
"""

ALL_VGS_OUTPUT = """
    Finding all volume groups
    Finding volume group "vg1"
    Finding volume group "data"
  VG|Attr|Ext|#PV|#LV|#SN|VSize|VFree|VG UUID
  data|wz--n-|4.00m|2|2|0|1020.00m|604.00m|DHbiyX-iY8b-Dr5t-3UYq-5kLp-3NiJ-qFFPYX
  vg1|wz--n-|4.00m|1|0|0|240.00m|240.00m|blUjZj-svFn-F4p1-o8sJ-SQxe-vEDh-dZCx7Z
"""

ONE_VGS_OUTPUT = """
    Using volume group(s) on command line
    Finding volume group "data"
  VG|Attr|Ext|#PV|#LV|#SN|VSize|VFree|VG UUID
  data|wz--n-|4.00m|2|2|0|1020.00m|604.00m|DHbiyX-iY8b-Dr5t-3UYq-5kLp-3NiJ-qFFPYX
"""

ALL_LVS_OUTPUT = """
    Finding all logical volumes
  LV|VG|#Seg|Attr|LSize|Maj|Min|KMaj|KMin|Origin|Snap%|Move|Copy%|Log|Convert|LV UUID
  lv1|data|1|-wi-a-|208.00m|-1|-1|252|2|||||||ib61dW-ePez-PLnN-u5pP-77PT-XygP-GNcjT1
  lv2|data|1|-wi-a-|208.00m|-1|-1|252|3|||||||5vm7vS-6O9C-A9jY-WbGP-Zaq5-kLGg-Q5URp6
  share|vg1|1|-wi-a-|104.00m|-1|-1|252|4|||||||XaSdDP-zyHl-p6i9-PWLX-pY30-jtuY-Ixvyn2
"""

ONE_LVS_OUTPUT = """
    Finding all logical volumes
  LV|VG|#Seg|Attr|LSize|Maj|Min|KMaj|KMin|Origin|Snap%|Move|Copy%|Log|Convert|LV UUID
  lv1|data|1|-wi-a-|208.00m|-1|-1|252|2|||||||ib61dW-ePez-PLnN-u5pP-77PT-XygP-GNcjT1
"""

class TestLinuxLVM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lvm = VolumeManager()

    def test__remove_headings_pvs_all(self):
        lines = self.lvm._remove_headings(ALL_PVS_OUTPUT, 'PV')
        self.assertEqual(5, len(lines))
        self.assertTrue(all([line.strip().startswith('/dev/') for line in lines]))

    def test__remove_headings_pvs_one(self):
        lines = self.lvm._remove_headings(ONE_PVS_OUTPUT, 'PV')
        self.assertEqual(1, len(lines))
        self.assertTrue(lines[0].strip().startswith('/dev/'))

    def test__remove_headings_vgs_all(self):
        lines = self.lvm._remove_headings(ALL_VGS_OUTPUT, 'VG')
        self.assertEqual(2, len(lines))
        self.assertTrue(all([line.strip().startswith('data') or line.strip().startswith('vg1') for line in lines]))

    def test__remove_headings_lvs_all(self):
        lines = self.lvm._remove_headings(ALL_LVS_OUTPUT, 'LV')
        self.assertEqual(3, len(lines))
        self.assertTrue(all([
            line.strip().startswith('lv1') or
            line.strip().startswith('lv2') or
            line.strip().startswith('share') for line in lines
            ]))

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_physical_volumes_all(self, run_cmd_mock):
        run_cmd_mock.return_value = ALL_PVS_OUTPUT
        pvs = self.lvm.get_physical_volumes()
        self.assertEqual(5, len(pvs))
        expected_pvs = [
                {'name': '/dev/sdd1', 'vg_name': 'data',
                    'size': '488.00m', 'uuid': 'Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll'},
                {'name': '/dev/sdd2', 'vg_name': 'data',
                    'size': '532.00m', 'uuid': '5b25y8-bRvk-m5Nb-rsRK-Wjqf-W34E-Hhpouo'},
                {'name': '/dev/sde1', 'vg_name': 'vg1', 'size': '200.00m', 'uuid': 'sde1'},
                {'name': '/dev/sde2', 'vg_name': None, 'size': '200.00m', 'uuid': 'sde2'},
                {'name': '/dev/sde3', 'vg_name': None, 'size': '200.00m', 'uuid': 'sde3'},
                ]
        for expected_pv, pv in map(None, expected_pvs, pvs):
            for attr in expected_pv:
                self.assertEqual(getattr(pv, attr, None), expected_pv[attr])

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_physical_volumes_by_name(self, run_cmd_mock):
        run_cmd_mock.return_value = ONE_PVS_OUTPUT
        pvs = self.lvm.get_physical_volumes(name='/dev/sdd1')
        self.assertEqual(1, len(pvs))
        expected_pvs = [
                {'name': '/dev/sdd1', 'vg_name': 'data',
                    'size': '488.00m', 'uuid': 'Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll'},
                ]
        for expected_pv, pv in map(None, expected_pvs, pvs):
            for attr in expected_pv:
                self.assertEqual(getattr(pv, attr, None), expected_pv[attr])

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_volume_groups_all(self, run_cmd_mock):
        run_cmd_mock.return_value = ALL_VGS_OUTPUT
        vgs = self.lvm.get_volume_groups()
        self.assertEqual(2, len(vgs))
        expected_vgs = [
                {'name': 'data', 'size': '1020.00m',
                    'uuid': 'DHbiyX-iY8b-Dr5t-3UYq-5kLp-3NiJ-qFFPYX'},
                {'name': 'vg1', 'size': '240.00m',
                    'uuid': 'blUjZj-svFn-F4p1-o8sJ-SQxe-vEDh-dZCx7Z'},
                ]

        for expected_vg, vg in map(None, expected_vgs, vgs):
            for attr in expected_vg:
                self.assertEqual(getattr(vg, attr, None), expected_vg[attr])

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_volume_groups_one(self, run_cmd_mock):
        run_cmd_mock.return_value = ONE_VGS_OUTPUT
        vgs = self.lvm.get_volume_groups()
        self.assertEqual(1, len(vgs))
        expected_vg = {
                    'name': 'data', 'size': '1020.00m',
                    'uuid': 'DHbiyX-iY8b-Dr5t-3UYq-5kLp-3NiJ-qFFPYX'
                    }

        for vg in vgs:
            for attr in expected_vg:
                self.assertEqual(getattr(vg, attr, None), expected_vg[attr])

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_logical_volumes_all(self, run_cmd_mock):
        run_cmd_mock.return_value = ALL_LVS_OUTPUT
        lvs = self.lvm.get_logical_volumes()
        self.assertEqual(3, len(lvs))

        expected_lvs = [
                {'name': 'lv1', 'vg_name': 'data', 'size': '208.00m',
                    'uuid': 'ib61dW-ePez-PLnN-u5pP-77PT-XygP-GNcjT1'},
                {'name': 'lv2', 'vg_name': 'data', 'size': '208.00m',
                    'uuid': '5vm7vS-6O9C-A9jY-WbGP-Zaq5-kLGg-Q5URp6'},
                {'name': 'share', 'vg_name': 'vg1', 'size': '104.00m',
                    'uuid': 'XaSdDP-zyHl-p6i9-PWLX-pY30-jtuY-Ixvyn2'},
                ]

        for expected_lv, lv in map(None, expected_lvs, lvs):
            for attr in expected_lv:
                self.assertEqual(getattr(lv, attr, None), expected_lv[attr])

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_logical_volumes_one(self, run_cmd_mock):
        run_cmd_mock.return_value = ONE_LVS_OUTPUT
        lvs = self.lvm.get_logical_volumes()
        self.assertEqual(1, len(lvs))
        expected_lv = {
                'name': 'lv1', 'vg_name': 'data', 'size': '208.00m',
                'uuid': 'ib61dW-ePez-PLnN-u5pP-77PT-XygP-GNcjT1'
                }

        for lv in lvs:
            for attr in expected_lv:
                self.assertEqual(getattr(lv, attr, None), expected_lv[attr])


class TestPhysicalVolumeLinuxLVM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        lvm = VolumeManager()
        cls.pv = PhysicalVolume(lvm, '/dev/sdd1', 'data', '488.00m',
                'Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll', 'dev')


    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_volume_group(self, run_cmd_mock):
        run_cmd_mock.return_value = ONE_VGS_OUTPUT
        vg = self.pv.get_volume_group()
        self.assertIsInstance(vg, VolumeGroup)
        self.assertEqual(vg.name, 'data')
        self.assertEqual(vg.size, '1020.00m')
        self.assertEqual(vg.uuid, 'DHbiyX-iY8b-Dr5t-3UYq-5kLp-3NiJ-qFFPYX')
