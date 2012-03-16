from dmtcore.disk.base import BasicDisk, DiskPartition

class LinuxDisk(BasicDisk):
    
    def __init__(self, disk_entry, hctl, uuid, disk_queries):
        super(LinuxDisk, self).__init__(disk_entry, hctl)
        self.uuid = uuid
        self.disk_queries = disk_queries

    def _generate_partitions(self):
        self.partitions = []
        for partition_entry in self.disk_queries.get_partition_entries(self.name):
            self.partitions.append(LinuxDiskPartition(partition_entry, self))

class LinuxDiskPartition(DiskPartition):

    def __init__(self, disk_entry, parent):
        super(LinuxDiskPartition, self).__init__(disk_entry, parent)