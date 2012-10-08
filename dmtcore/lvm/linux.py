from dmtcore.os.commands import run_cmd
from dmtcore.lvm.api import PhysicalVolume

class VolumeManager(object):


    def get_physical_volumes(self, name=None):
        pvs = []
        cmd = ['pvs', '-v', '--separator', '|']
        if name:
            cmd.append(name)
        for line in run_cmd(cmd).strip().splitlines()[2:]:
            pv, vg, fmt, attr, psize, pfree, devsize, uuid = line.strip().split('|')
            pvs.append(PhysicalVolume(lvm=self, name=pv, vg=vg, size=psize, uuid=uuid, device='dev'))
        return pvs

    def get_volume_groups(self, name=None):
        return []

    def get_logical_volumes(self, name=None):
        return []


