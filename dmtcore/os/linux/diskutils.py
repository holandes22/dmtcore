from dmtcore.os.cmd import FDISK_LIST
from dmtcore.os.os_command import os_command

def list_disks():
    return os_command(FDISK_LIST)
