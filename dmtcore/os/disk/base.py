"""
Interfaces for classes in charge of detecting the disk devices and populating the information.
"""
from collections import namedtuple

HctlInfo = namedtuple("HctlInfo", "host,channel,scsi_id,lun_id")

class DiskEntry(object):
    
    def __init__(self, name, filepath, raw_filepath, size, hctl):
        self.name = name
        self.filepath = filepath
        self.raw_filepath = raw_filepath
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
                
    def _populate_disks_entries(self):
        raise NotImplementedError()
    
    def _get_partition_entries(self, device_name):
        raise NotImplementedError()
    
    def _get_path_entries(self, device_name):
        raise NotImplementedError()