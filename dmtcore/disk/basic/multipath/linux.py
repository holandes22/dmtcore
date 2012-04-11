from dmtcore.disk.base import MultipathDisk, Path, PathGroup


class LinuxMultipathDisk(MultipathDisk):

    def __init__(self, disk_entry):
        super(LinuxMultipathDisk, self).__init__(disk_entry)
        self.wwid = disk_entry.mp_details.wwid
        """WWID of the device"""
        self.vendor = disk_entry.mp_details.vendor
        """Vendor of the device"""
        self.sysfs_name = disk_entry.mp_details.sysfs_name
        """sysfs name, dm-xx"""
        self.alias = disk_entry.mp_details.alias
        """Alias used if friendly names is set to yes"""

    def _generate_paths(self):
        self.paths = []
        self.path_groups = []


class LinuxPath(Path):

    def __init__(self, path_entry, name):
        super(LinuxPath, self).__init__(path_entry)
        self.name = name


class LinuxPathGroup(PathGroup):

    def __init__(self, paths, state, priority, selector, repeat_count):
        super(LinuxPathGroup, self).__init__(paths)
        self.state = state
        self.priority = priority
        self.selector = selector
        self.repeat_count = repeat_count
