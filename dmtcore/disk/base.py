class Disk(object):
    
    def __init__(self, disk_entry):
        self._name = disk_entry.name
        self._filepath = disk_entry.filepath
        self._size = disk_entry.size
        self._uuid = disk_entry.uuid
        self._major_minor = disk_entry.major_minor
        """Tuple of major and minor numbers"""
        self._hctl = disk_entry.hctl
        """SCSI info: host, channel, scsi_id and lun"""
        
    @property
    def name(self):
        return self._name

    @property
    def filepath(self):
        return self._filepath
    
    @property
    def size(self):
        return self._size

class DiskPartition(Disk):
    
    def __init__(self, disk_entry, parent):
        super(DiskPartition, self).__init__(disk_entry)
        self.parent = parent

class BasicDisk(Disk):

    def __init__(self, disk_entry):
        super(BasicDisk, self).__init__(disk_entry)
        self._generate_partions()

    def get_partitions(self):
        return self.partitions

    def _generate_partitions(self):
        raise NotImplementedError()

class MultipathDisk(BasicDisk):
    
    def __init__(self, disk_entry):
        super(MultipathDisk, self).__init__(disk_entry)
        self._generate_paths()

    def _generate_paths(self):
        """Populates the path and path_groups properties"""
        raise NotImplementedError()

    def get_path_groups(self):
        """
        :return: A list of :py:class:`PathGroup` objects.
        """
        return self.path_groups

    def get_paths(self):
        return self.paths

    def get_path_count(self):
        return len(self.paths)

    def get_active_path_count(self):
        return len([path for path in self.paths if path.is_active()])

class Path(Disk):

    def __init__(self, disk_entry, path_entry):
        super(Path, self).__init__(disk_entry)
        self._state = path_entry.state
        """Physical path state"""
        self._mapper_path_state = path_entry.mapper_path_state
        """Mapper path state. e.g. DM on Linux"""

    def is_active(self):
        return self._state == 'active'

class PathGroup(object):

    def __init__(self, paths):
        self._paths = paths
    
    @property
    def paths(self):
        return self._paths


def get_disks():
    return []


