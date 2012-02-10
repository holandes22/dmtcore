class Disk(object):
    
    def __init__(self, disk_entry):
        self.name = disk_entry.name
        self.filepath = disk_entry.filepath
        self.size = disk_entry.size
        self.major_minor = disk_entry.major_minor

    def get_name(self):
        return self.name

    def get_filepath(self):
        return self.filepath

    def get_size(self):
        return self.size

    def get_major_minor(self):
        """
        Tuple of major and minor numbers
        """
        return self.major_minor


class DiskPartition(Disk):
    
    def __init__(self, disk_entry, parent):
        super(DiskPartition, self).__init__(disk_entry)
        self.parent = parent

class BasicDisk(Disk):

    def __init__(self, disk_entry, hctl):
        super(BasicDisk, self).__init__(disk_entry)
        self.hctl = hctl
        self.partitions = None
        

    def get_partitions(self):
        if getattr(self, 'partitions', None) is None:
            self._generate_partitions()
        return self.partitions

    def _generate_partitions(self):
        raise NotImplementedError()
    
    def get_hctl(self):
        """
        SCSI info: host, channel, scsi_id and lun
        """
        return self.hctl

class MultipathDisk(BasicDisk):
    
    def __init__(self, disk_entry):
        super(MultipathDisk, self).__init__(disk_entry)
        self.paths = None
        self.path_groups = None
        self._generate_paths()

    def _generate_paths(self):
        """
        Populates the path and path_groups properties
        """
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

class Path(object):

    def __init__(self, path_entry):
        self.state = path_entry.state
        """Physical path state"""
        self.mapper_path_state = path_entry.mapper_path_state
        """Mapper path state. e.g. DM on Linux"""

    def is_active(self):
        return self.state == 'active'

class PathGroup(object):

    def __init__(self, paths):
        self.paths = paths

def get_disks():
    return []


