import unittest
from mock import patch
from dmtcore.lvm.linux import VolumeManager

ALL_PVS_OUTPUT = """
   Scanning for physical volume names
    PV|VG|Fmt|Attr|PSize|PFree|DevSize|PV UUID
    /dev/sdd1|data|lvm2|a-|488.00m|72.00m|488.28m|Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll
    /dev/sdd2|data|lvm2|a-|532.00m|532.00m|534.72m|5b25y8-bRvk-m5Nb-rsRK-Wjqf-W34E-Hhpouo
"""

ONE_PVS_OUTPUT = """
   Scanning for physical volume names
    PV|VG|Fmt|Attr|PSize|PFree|DevSize|PV UUID
    /dev/sdd1|data|lvm2|a-|488.00m|72.00m|488.28m|Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll
"""

class TestLinuxLVM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lvm = VolumeManager()

    @patch("dmtcore.lvm.linux.run_cmd")
    def test_get_physical_volumes_all(self, run_cmd_mock):
        run_cmd_mock.return_value = ALL_PVS_OUTPUT
        pvs = self.lvm.get_physical_volumes()
        self.assertEqual(2, len(pvs))
        expected_pvs = [
                {'name': '/dev/sdd1', 'vg': 'data',
                    'size': '488.00m', 'uuid': 'Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll'},
                {'name': '/dev/sdd2', 'vg': 'data',
                    'size': '532.00m', 'uuid': '5b25y8-bRvk-m5Nb-rsRK-Wjqf-W34E-Hhpouo'},
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
                {'name': '/dev/sdd1', 'vg': 'data',
                    'size': '488.00m', 'uuid': 'Lqnjui-WoJW-1VcW-O3hT-cUaL-Rkfe-6km7Ll'},
                ]
        for expected_pv, pv in map(None, expected_pvs, pvs):
            for attr in expected_pv:
                self.assertEqual(getattr(pv, attr, None), expected_pv[attr])
