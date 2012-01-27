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

DEV_ROOT_PATH = '/dev'

SIZE_FROM_FDISK = ['/sbin/fdisk', '-l']

class LinuxDiskEntry(DiskEntry):
    
    def __init__(self, name, filepath, size, hctl, uuid):
        super(LinuxDiskEntry, self).__init__(name, filepath, size, hctl)
        self.uuid = uuid

class LinuxDiskDeviceQueries(DiskDeviceQueries):
    
    def _populate_disks_entries(self):
        for filepath in glob('%s/sd*[!0-9]' % DEV_ROOT_PATH):
            name = filepath[len(DEV_ROOT_PATH):]
            size = self._extract_size_from_fdisk(filepath)
            h, c, t, l = self.extract_hctl_from_sys_folder(name)
            hctl = HctlInfo(host = h, channel = c, scsi_id = t, lun_id = l)
            self.basic_disk_entries.append(DiskEntry(name, filepath, size, hctl ))
    
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
        for line in run_cmd(SIZE_FROM_FDISK).split("\n"):
            if dev_re.match(line) is not None:
                size = line.split(",")[1].split()[0]
                try:
                    return int(size)
                except ValueError:
                    return None    
        return None
    
    def _extract_hctl_from_sys_folder(self, device_name):
        pass