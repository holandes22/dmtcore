
from dmtcore.os.disk.linux import LinuxDiskDeviceQueries
from dmtcore.disk.base import BasicDisk, DiskPartition, MultipathDisk, Path, PathGroup

def get_all_disks():
    all_disks = []
    linux_disk_device_queries = LinuxDiskDeviceQueries()
    for basic_disk_entry in linux_disk_device_queries.get_basic_disk_entries():
        hctl = linux_disk_device_queries.get_hctl(basic_disk_entry.name)
        all_disks.append(LinuxDisk(basic_disk_entry, hctl, "fake-uuid"))
    return all_disks

class LinuxDisk(BasicDisk):
    
    def __init__(self, disk_entry, hctl, uuid):
        super(LinuxDisk, self).__init__(disk_entry, hctl)
        self.uuid = uuid

    def _generate_partitions(self):
        self.partitions = []

class LinuxDiskPartition(DiskPartition):

    def __init__(self, disk_entry, parent):
        super(LinuxDiskPartition, self).__init__(disk_entry, parent)

class MultipathLinuxDisk(MultipathDisk):
    
    def __init__(self, disk_entry, wwid, vendor, sysfs_name, alias):
        super(MultipathLinuxDisk, self).__init__(disk_entry)
        self.wwid = wwid
        self.vendor = vendor
        self.sysfs_name = sysfs_name
        self.alias = alias

    def _generate_paths(self):
        self.paths = []
        self.path_groups = []


class LinuxPath(Path):

    def __init__(self, path_entry):
        super(LinuxPath, self).__init__(path_entry)

class LinuxPathGroup(PathGroup):

    def __init__(self, paths, state, priority, selector, repeat_count, level):
        super(LinuxPathGroup, self).__init__(paths)
        self.state = state
        self.priority = priority
        self.selector = selector
        self.repeat_count = repeat_count
        self.level = level
