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
        self.path_group_entries = disk_entry.path_groups

    def _generate_paths(self):
        self.paths = []
        self.path_groups = []
        for path_group_entry in self.path_group_entries:
            paths = [LinuxPath(path_entry) for path_entry in path_group_entry.paths]
            self.path_groups.append(LinuxPathGroup(paths, path_group_entry))
            self.paths.extend(paths)


class LinuxPath(Path):

    def __init__(self, path_entry):
        super(LinuxPath, self).__init__(path_entry)
        self.mapper_path_state = path_entry.mapper_path_state
        """Mapper path state. e.g. DM on Linux"""
        self.name = path_entry.name


class LinuxPathGroup(PathGroup):

    def __init__(self, paths, linux_path_group_entry):
        super(LinuxPathGroup, self).__init__(paths)
        self.state = linux_path_group_entry.state
        self.priority = linux_path_group_entry.priority
        self.selector = linux_path_group_entry.selector
        self.count = linux_path_group_entry.count
        """Repeat count"""
