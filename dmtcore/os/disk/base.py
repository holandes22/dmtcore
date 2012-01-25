"""
Interfaces for classes in charge of detecting the disk devices and populating the information.
"""
from collections import namedtuple

HctlInfo = namedtuple("HctlInfo", "host,channel,scsi_id,lun_id")

class DiskEntry(object):
    
    def __init__(self, name, filepath, size, hctl):
        self.name = name
        self.filepath = filepath
        self.size = size
        self.hctl = hctl
        
class PathEntry(object):
    
    def __init__(self, state):
        self.state = state

class DiskDeviceQueries(object):
    
    def __init__(self):
        self.basic_disk_entries = []
        self.multipath_disk_entries = []
        self._populate_disks_entries()
        
    def get_basic_disk_entries(self):
        return self.basic_disk_entries
    
    def get_multipath_disk_entries(self):
        return self.multipath_disk_entries
                
    def _populate_disks_entries(self):
        raise NotImplementedError()
    
    def _get_partition_entries(self, device_name):
        raise NotImplementedError()
    
    def _get_path_entries(self, device_name):
        raise NotImplementedError()