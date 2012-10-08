from dmtcore.os.commands import run_cmd
from dmtcore.lvm.api import PhysicalVolume, VolumeGroup, LogicalVolume

PARSE_SEPARATOR = '|'
PARSE_OPTS = ['-v', '--separator', PARSE_SEPARATOR]


class VolumeManager(object):

    def _remove_headings(self, output, header_start):
        # vgs, pvs, lvs command don't have an option to remove informative crap
        # at beginning, which can vary in line amount
        lines = output.strip().splitlines()
        count = 0
        for line in lines:
            if line.strip().startswith(header_start):
                break
            count += 1
        return lines[count + 1:]

    def get_physical_volumes(self, name=None):
        pvs = []
        cmd = ['pvs'] + PARSE_OPTS
        if name:
            cmd.append(name)
        for line in self._remove_headings(run_cmd(cmd).strip(), 'PV'):
            pv, vg, fmt, attr, psize, pfree, devsize, uuid = line.strip().split('|')
            if vg == '':
                vg = None
            pvs.append(PhysicalVolume(lvm=self, name=pv, vg_name=vg,
                size=psize, uuid=uuid, device='dev'))
        return pvs

    def get_volume_groups(self, name=None):
        vgs = []
        cmd = ['vgs'] + PARSE_OPTS
        if name:
            cmd.append(name)
        for line in self._remove_headings(run_cmd(cmd).strip(), 'VG'):
            # VG|Attr|Ext|#PV|#LV|#SN|VSize|VFree|VG UUID
            vg, attr, ext, npv, nlv, nsn, size, free, uuid = line.strip().split('|')
            vgs.append(VolumeGroup(lvm=self, name=vg, size=size, uuid=uuid))
        return vgs

    def get_logical_volumes(self, name=None):
        lvs = []
        cmd = ['lvs'] + PARSE_OPTS
        if name:
            cmd.append(name)
        for line in self._remove_headings(run_cmd(cmd).strip(), 'LV'):
            #  LV|VG|#Seg|Attr|LSize|Maj|Min|KMaj|KMin|Origin|Snap%|Move|Copy%|Log|Convert|LV UUID
            lv, vg, nseg, attr, size, maj, _min, kmaj, kmin, orig,\
                snap_per, move, copy_per, log, convert, uuid  = line.strip().split('|')
            lvs.append(LogicalVolume(lvm=self, name=lv, vg_name=vg, size=size, uuid=uuid))
        return lvs
