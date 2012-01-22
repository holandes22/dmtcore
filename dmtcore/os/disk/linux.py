from glob import glob

from dmtcore.os.disk.base import DiskDeviceQueries
from dmtcore.os.disk.base import DiskEntry


DISK_LINUX_CMDS = [
                   [],
                   ]
DEV_ROOT_PATH = '/dev/'

class LinuxDiskDeviceQueries(DiskDeviceQueries):
    
    def _populate_disks_entries(self):
        for file_path in glob('/dev/sd*[!0-9]'):
            name = file_path[len('/dev/'):]
            self.basic_disk_entries.append(DiskEntry())
        