from dmtcore.disk.base import MultipathDisk, Path, PathGroup

class LinuxMultipathDisk(MultipathDisk):
    
    def __init__(self, disk_entry, wwid, vendor, sysfs_name, alias):
        super(LinuxMultipathDisk, self).__init__(disk_entry)
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