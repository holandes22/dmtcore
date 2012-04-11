from dmtcore.os.disk.linux import LinuxDiskDeviceQueries
from dmtcore.disk.basic.linux import LinuxDisk
from dmtcore.disk.basic.multipath.linux import LinuxMultipathDisk


def get_disks():
    basic_disks = []
    multipath_disks = []
    linux_disk_device_queries = LinuxDiskDeviceQueries()
    mp_disk_path_devnos = []
    for multipath_disk_entry in linux_disk_device_queries.get_multipath_disk_entries():
        mp_disk_path_devnos.append(multipath_disk_entry.major_minor)
        multipath_disks.append(LinuxMultipathDisk(multipath_disk_entry))

    for basic_disk_entry in linux_disk_device_queries.get_basic_disk_entries():
        if basic_disk_entry.major_minor in mp_disk_path_devnos:
            # disk is a path of a multi path disk
            continue
        uuid = linux_disk_device_queries.get_uuid(basic_disk_entry.filepath)
        basic_disks.append(LinuxDisk(basic_disk_entry, uuid, linux_disk_device_queries))
    return basic_disks + multipath_disks
