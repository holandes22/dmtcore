from dmtcore.os.disk.linux import LinuxDiskDeviceQueries
from dmtcore.disk.basic.linux import LinuxDisk
from dmtcore.disk.basic.multipath.linux import LinuxMultipathDisk


def get_disks():
    basic_disks = []
    multipath_disks = []
    linux_disk_device_queries = LinuxDiskDeviceQueries()
    mp_disk_path_names = []
    for multipath_disk_entry in linux_disk_device_queries.get_multipath_disk_entries():
        for path_group in multipath_disk_entry.path_groups:
            mp_disk_path_names.extend([path.name for path in path_group.paths])
        multipath_disks.append(LinuxMultipathDisk(multipath_disk_entry))

    for basic_disk_entry in linux_disk_device_queries.get_basic_disk_entries():
        if basic_disk_entry.name in mp_disk_path_names:
            # disk is a path of a multi path disk
            continue
        uuid = linux_disk_device_queries.get_uuid(basic_disk_entry.filepath)
        basic_disk_entry.disk_identifier = linux_disk_device_queries.get_disk_identifier(basic_disk_entry.filepath)
        basic_disks.append(LinuxDisk(basic_disk_entry, uuid, linux_disk_device_queries))
    return basic_disks + multipath_disks
