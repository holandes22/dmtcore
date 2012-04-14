class Disk(object):
    """
    Base interface for disk objects
    """

    def __init__(self, disk_entry):
        self.name = disk_entry.name
        self.filepath = disk_entry.filepath
        self.size = disk_entry.size
        self.major_minor = disk_entry.major_minor
        self.hctl = disk_entry.hctl

    def get_name(self):
        return self.name

    def get_filepath(self):
        return self.filepath

    def get_size(self):
        return self.size

    def get_major_minor(self):
        """
        Named tuple of major and minor numbers
        """
        return self.major_minor

    def get_hctl(self):
        """
        SCSI info: host, channel, scsi_id and lun
        """
        return self.hctl


class DiskPartition(Disk):

    def __init__(self, disk_entry, parent):
        super(DiskPartition, self).__init__(disk_entry)
        self.parent = parent


class BasicDisk(Disk):
    """
    Represents a basic (local, non-multipath) disk
    """

    def __init__(self, disk_entry):
        super(BasicDisk, self).__init__(disk_entry)
        self.partitions = None
        self.disk_identifier = disk_entry.disk_identifier

    def get_partitions(self):
        if getattr(self, 'partitions', None) is None:
            self._generate_partitions()
        return self.partitions

    def _generate_partitions(self):
        raise NotImplementedError()


class MultipathDisk(Disk):

    def __init__(self, disk_entry):
        super(MultipathDisk, self).__init__(disk_entry)
        self.paths = None
        self.path_groups = None

    def _generate_paths(self):
        """
        Populates the path and path_groups properties
        """
        raise NotImplementedError()

    def get_path_groups(self):
        """
        :return: A list of :py:class:`PathGroup` objects.
        """
        if not self.path_groups:
            self._generate_paths()
        return self.path_groups

    def get_paths(self):
        if not self.paths:
            self._generate_paths()
        return self.paths

    def get_path_count(self):
        return len(self.get_paths())

    def get_active_path_count(self):
        return len([path for path in self.get_paths() if path.is_active()])


class Path(object):
    """
    Represents a path on a multipath disk
    """

    def __init__(self, path_entry):
        self.physical_state = path_entry.physical_state
        """Physical path state"""

    def is_active(self):
        return self.physical_state == 'active'


class PathGroup(object):
    """
    Represents a group of paths from a multipath disk.
    This is not neccessarily relevant for all platforms (Linux has this concept, but HP-UX no for instance)
    """
    def __init__(self, paths):
        self.paths = paths
