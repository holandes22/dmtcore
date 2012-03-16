from dmtcore.os.disk.linux import LinuxDiskDeviceQueries
from dmtcore.disk.basic.linux import LinuxDisk
from dmtcore.disk.basic.multipath.linux import LinuxMultipathDisk

def get_disks():
    all_disks = []
    linux_disk_device_queries = LinuxDiskDeviceQueries()
    for basic_disk_entry in linux_disk_device_queries.get_basic_disk_entries():
        hctl = linux_disk_device_queries.get_hctl(basic_disk_entry.name)
        all_disks.append(LinuxDisk(basic_disk_entry, hctl, "fake-uuid", linux_disk_device_queries))
    return all_disks




