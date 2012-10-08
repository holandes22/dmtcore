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

    def __init__(self, lvm, name, vg_name, size, uuid, device):
        self.lvm = lvm
        self.name = name
        self.vg_name = vg_name
        self.size = size
        self.uuid = uuid
        self.device = device

    def get_volume_group(self):
        if self.vg_name is not None:
            return self.lvm.get_volume_groups(name=self.vg_name)[0]
        return None

    def get_free_size(self):
        return self.lvm.get_pv_free_size(pv=self.name)


class VolumeGroup(object):

    def __init__(self, lvm, name, size, uuid):
        self.lvm = lvm
        self.name = name
        self.size = size
        self.uuid = uuid

    def get_physical_volumes(self):
        return self.lvm.get_pvs_by_vg(name=self.name)

    def get_logical_volumes(self):
        return self.lvm.get_lvs_by_vg(name=self.name)

    def get_free_size(self):
        return self.lvm.get_vg_free_size(vg=self.name)


class LogicalVolume(object):

    def __init__(self, lvm, name, vg_name, size, uuid):
        self.lvm = lvm
        self.name = name
        self.vg_name = vg_name
        self.size = size
        self.uuid = uuid

    def get_volume_group(self):
        return self.lvm.get_volume_groups(name=self.name)[0]
