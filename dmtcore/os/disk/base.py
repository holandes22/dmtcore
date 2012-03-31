"""
Interfaces for classes in charge of detecting the disk devices and populating the information.
"""
from collections import namedtuple

HctlInfo = namedtuple("HctlInfo", "host,channel,scsi_id,lun_id")

class DiskEntry(object):
    
    def __init__(self, name, filepath, size, major_minor, hctl):
        self.name = name
        self.filepath = filepath
        self.size = size
        self.major_minor = major_minor
        self.hctl = hctl
        
    def __str__(self):
        return "%s(name=%s, filepath=%s, size=%s, major_minor=%s, hctl=%s)" % (
                                                                      self.__class__.__name__, 
                                                                      self.name,
                                                                      self.filepath,
                                                                      self.size,
                                                                      self.major_minor,
                                                                      self.hctl
                                                                      )

        
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
                
    def get_partition_entries(self, device_name):
        raise NotImplementedError()
    
    def get_path_entries(self, device_name):
        raise NotImplementedError()
    
    def get_path_group_entries(self, device_name):
        raise NotImplementedError()
    
    def _populate_disks_entries(self):
        raise NotImplementedError()