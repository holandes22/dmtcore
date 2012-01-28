import os
import re
from glob import glob

from dmtcore.os.commands import run_cmd
from dmtcore.os.disk.base import DiskDeviceQueries
from dmtcore.os.disk.base import DiskEntry, HctlInfo

#From dmtcore.os.linux.basic
#from dmtcore.os.commands import run_cmd, FDISK_LIST
#
#def list_disks():
#    return "NEW - %s" % (run_cmd(FDISK_LIST),)

SIZE_FROM_FDISK = ['/sbin/fdisk', '-l']

class LinuxDiskEntry(DiskEntry):
    
    def __init__(self, name, filepath, size, uuid):
        super(LinuxDiskEntry, self).__init__(name, filepath, size)
        self.uuid = uuid

class LinuxDiskDeviceQueries(DiskDeviceQueries):
    
    def _populate_disks_entries(self):
        disk_names = []
        for filepath in glob('/dev/sd*[!0-9]'):
            name = os.path.basename(filepath)
            disk_names.append(name)
            size = self._extract_size_from_fdisk(filepath)
            h, c, t, l = self.get_hctl(name)
            hctl = HctlInfo(host = h, channel = c, scsi_id = t, lun_id = l)
            self.basic_disk_entries.append(DiskEntry(name, filepath, size, hctl ))
        
        self.hctl_map = self._map_hctl_to_disk_device_names(disk_names)
    
    def _device_name_is_partition(self, device_name):
        """
        Receives a device name and indicates if it is a partition or not:
        sda -> False
        sdab11 -> True
        sda1b, /dev/sda1 ->False, not valid input
        """
        return  re.compile("^\w+\d+$").match(device_name) is not None
    
    def _extract_size_from_fdisk(self, device_filepath):
        """
        :returns: The size in bytes of the specified device
        :rtype: int or None if an error occured obtaining the value
        """
        #parse Disk /dev/sda: 8185 MB, 8185184256 bytes
        dev_re = re.compile("^Disk\s\/dev\/sd.*$")
        for line in run_cmd(SIZE_FROM_FDISK + [device_filepath]).splitlines():
            if dev_re.match(line) is not None:
                size = line.split(",")[1].split()[0]
                try:
                    return int(size)
                except ValueError:
                    return None    
        return None
    
    def get_hctl(self, device_name):
        try:
            return self.hctl_map[device_name]
        except KeyError:
            return None
    
    def _get_all_hctls(self):
        if getattr(self, '_all_hctls', None) is None:
            self._all_hctls =  self._extract_all_hctls_from_proc_scsi_file()
        return self._all_hctls 
  
    def _map_hctl_to_disk_device_names(self, device_names):
        hctl_map = {}
        for device_name in device_names:
            for hctl in self._get_all_hctls():
                d =  {'name': device_name,'h': hctl.host, 'c': hctl.channel, 't': hctl.scsi_id, 'l': hctl.lun_id}
                path = "/sys/block/{name}/device/scsi_disk:{h}:{c}:{t}:{l}".format(**d)
                if os.path.exists(path):
                    hctl_map[device_name] = hctl
        return hctl_map
    
    def _extract_all_hctls_from_proc_scsi_file(self):
        hctls = []
        hctl_line_re= re.compile("""
                                    Host:\s*\w*(?P<host>\d+)\s*
                                    Channel:\s*(?P<channel>\d+)\s*
                                    Id:\s*(?P<scsi_id>\d+)\s*
                                    Lun:\s+(?P<lun_id>\d+)\s*
                                """, re.VERBOSE)

        
        with open("/proc/scsi/scsi", "r") as f:
            for line in f.readlines():
                m = hctl_line_re.match(line)
                if m is not None:
                    hctls.append(
                                 HctlInfo(
                                          host = int(m.group("host")),
                                          channel = int(m.group("channel")),
                                          scsi_id = int(m.group("scsi_id")),
                                          lun_id = int(m.group("lun_id"))
                                          )
                                 )
        return hctls
    
