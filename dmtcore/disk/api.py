from dmtcore.os.platimport import platimport

def get_disks():
    platform_get_disks = platimport("dmtcore.disk", "get_disks")
    return platform_get_disks()
