from dmtcore.disk.base import BasicDisk, DiskPartition, MultipathDisk, Path, PathGroup

def get_all_disks():
    pass


class LinuxDisk(BasicDisk):
    
    def __init__(self, disk_entry):
        super(LinuxDisk, self).__init__(disk_entry)

    def _generate_partitions(self):
        self.partitions = []


class LinuxDiskPartition(DiskPartition):

    def __init__(self, disk_entry, parent):
        super(LinuxDiskPartition, self).__init__(disk_entry, parent)


class MultipathLinuxDisk(MultipathDisk):
    
    def __init__(self, disk_entry, wwid, vendor, sysfs_name, alias):
        super(MultipathLinuxDisk, self).__init__(disk_entry)
        self._wwid = wwid
        self._vendor = vendor
        self._sysfs_name = sysfs_name
        self._alias = alias

    def _generate_paths(self):
        self.paths = []
        self.path_groups = []

    @property
    def wwid(self):
        return self._wwid


class LinuxPath(Path):

    def __init__(self, disk_entry, path_entry):
        super(LinuxPath, self).__init__(disk_entry, path_entry)


class LinuxPathGroup(PathGroup):

    def __init__(self, paths, state, priority, selector, repeat_count, level):
        super(LinuxPathGroup, self).__init__(paths)
        self._state = state
        self._priority = priority
        self._selector = selector
        self._repeat_count = repeat_count
        self._level = level
