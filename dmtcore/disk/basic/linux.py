from dmtcore.disk.base import BasicDisk, DiskPartition

class LinuxDisk(BasicDisk):
    
    def __init__(self, disk_entry, hctl, uuid, disk_queries):
        super(LinuxDisk, self).__init__(disk_entry, hctl)
        self.uuid = uuid
        self.disk_queries = disk_queries

    def get_uuid(self):
        return self.uuid

    def _generate_partitions(self):
        self.partitions = []
        print self.disk_queries.uuid_map
        for partition_entry in self.disk_queries.get_partition_entries(self.name):
            uuid = self.disk_queries.get_uuid(partition_entry.filepath)
            self.partitions.append(LinuxDiskPartition(partition_entry, self, uuid))

class LinuxDiskPartition(DiskPartition):

    def __init__(self, disk_entry, parent, uuid):
        super(LinuxDiskPartition, self).__init__(disk_entry, parent)
        self.uuid = uuid
        
    def get_uuid(self):
        return self.uuid    