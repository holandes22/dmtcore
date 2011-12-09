from dmtcore.os.commands import run_cmd, FDISK_LIST

def list_disks():
    return "NEW - %s" % (run_cmd(FDISK_LIST),)
