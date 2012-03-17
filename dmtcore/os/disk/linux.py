import os
import re
import logging
from glob import glob

from dmtcore.os.disk.common import get_major_minor

from dmtcore.os.commands import run_cmd
from dmtcore.os.commands import SIZE_FROM_FDISK, BLKID

from dmtcore.os.disk.base import DiskDeviceQueries
from dmtcore.os.disk.base import DiskEntry, HctlInfo

module_logger = logging.getLogger("dmtcore.os.disk.linux")

class LinuxDeviceMapper(object):
    pass

class LinuxDiskDeviceQueries(DiskDeviceQueries):

    def _populate_disks_entries(self):
        device_filepaths = glob('/dev/sd*[!0-9]')
        device_names = [os.path.basename(device_filepath) for device_filepath in device_filepaths]
        self.hctl_map = self._map_hctl_to_disk_device_names(device_names)

        for device_filepath, device_name in map(None, device_filepaths, device_names):
            size = self._extract_size_from_fdisk(device_filepath)
            major_minor = get_major_minor(device_filepath)
            self.basic_disk_entries.append(DiskEntry(device_name, device_filepath, size, major_minor))

        self.multipath_disk_entries = []

    def get_partition_entries(self, device_name):
        return self._get_sysfs_partitions(device_name)

    def _get_sysfs_partitions(self, device_name):
        partitions = []
        partition_filepaths = glob('/dev/%s[0-9]*' % device_name)
        for partition_filepath in partition_filepaths:
            size = self._extract_size_from_fdisk(partition_filepath)
            major_minor = get_major_minor(partition_filepath)
            partitions.append(DiskEntry(
                                        os.path.basename(partition_filepath),
                                        partition_filepath,
                                        size,
                                        major_minor,
                                        )
                              )
        return partitions

    def _device_name_is_partition(self, device_name):
        """
        Receives a device name and indicates if it is a partition or not:
        sda -> False
        sdab11 -> True
        sda1b, /dev/sda1 ->False, not valid input
        """
        return  re.compile("^\w+\d+$").match(device_name) is not None

    def _extract_size_from_fdisk(self, device_filepath):
        """/sys/block/sda/device/block/sda
        :returns: The size in bytes of the specified device
        :rtype: int or None if an error occured obtaining the value
        """
        #parse Disk /dev/sda: 8185 MB, 8185184256 bytes
        dev_re = re.compile("^Disk\s\/dev\/sd.*:")
        for line in run_cmd(SIZE_FROM_FDISK + [device_filepath]).splitlines():
            if dev_re.match(line) is not None:
                size = line.split(",")[1].split()[0]
                try:
                    return int(size)
                except ValueError:
                    module_logger.warning("Cannot get size for device {0}.\
                                                            Output: {1}".format(device_filepath, size))
                    return None
        return None

    def get_hctl(self, device_name):
        try:
            return self.hctl_map[device_name]
        except KeyError:
            module_logger.warning("Cannot get hctl for device {0}".format(device_name))
            return None

    def _map_hctl_to_disk_device_names(self, device_names):
        hctl_map = {}
        for device_name in device_names:
            hctl_map[device_name] = self._extract_hctl_from_device_link(device_name)
        return hctl_map

    def _extract_hctl_from_device_link(self, device_name):
        path = "/sys/block/{0}/device".format(device_name)
        try:
            h,c,t,l = os.readlink(path).split("/")[-1].split(":")
        except OSError:
            return None
        return HctlInfo(int(h),int(c),int(t),int(l))

    def _extract_all_hctls_from_proc_scsi_file(self):
        hctls = []
        hctl_line_re= re.compile("""
                                    Host:\s*\w*(?P<host>\d+)\s*
                                    Channel:\s*(?P<channel>\d+)\s*
                                    Id:\s*(?P<scsi_id>\d+)\s*
                                    Lun:\s+(?P<lun_id>\d+)\s*
                                """, re.VERBOSE)


        with open("/proc/scsi/scsi", "r") as f:
            for line in f.readlines():
                m = hctl_line_re.match(line)
                if m is not None:
                    hctls.append(
                                 HctlInfo(
                                          host = int(m.group("host")),
                                          channel = int(m.group("channel")),
                                          scsi_id = int(m.group("scsi_id")),
                                          lun_id = int(m.group("lun_id"))
                                          )
                                 )
        return hctls
    
    def _extract_uuid_from_blkid(self, device_filepath):
        uuid_re = re.compile("^UUID=(?P<uuid>.*)$")
        for line in run_cmd(BLKID + [device_filepath]).splitlines():
            m = uuid_re.match(line)
            if m  is not None:
                return m.group("uuid")
        return None

