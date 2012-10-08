from dmtcore.os.platimport import platimport


class VolumeManager(object):

    def __init__(self):
        self.implementor = platimport("dmtcore.lvm", "VolumeManager")()

    def get_physical_volumes(self):
        return self.implementor.get_physical_volumes()

    def get_volume_groups(self):
        return self.implementor.get_volume_groups()

    def get_logical_volumes(self):
        return self.implementor.get_logical_volumes()


class PhysicalVolume(object):

    def __init__(self, lvm, name, vg, size, uuid, device):
        self.lvm = lvm
        self.name = name
        self.vg = vg
        self.size = size
        self.uuid = uuid
        self.device = device

    def get_volume_group(self):
        return self.vg


class VolumeGroup(object):

    def __init__(self, lvm, name, size, free, uuid):
        self.lvm = lvm
        self.name = name
        self.size = size
        self.free = free
        self.uuid = uuid

    def get_physical_volumes(self):
        return self.lvm.get_physical_volumes(name=self.name)

    def get_logical_volumes(self):
        return self.lvm.get_logical_volumes(name=self.name)


class LogicalVolume(object):

    def __init__(self, lvm, name, vg, size, uuid):
        self.lvm = lvm
        self.name = name
        self.vg = vg
        self.size = size
        self.uuid = uuid

    def get_volume_group(self):
        return self.vg
