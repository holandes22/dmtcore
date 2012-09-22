import platform
from collections import namedtuple

PlatformDetails = namedtuple("PlatformDetails", "architecture,machine,processor,system,hostname,release")
SUPPORTED_PLATFORMS = [
                       "linux",
                       ]

SUPPORTED_DISTROS = {
                     "centos": [5, 6],
                     "rhel": [5, 6],
                     "debian": [6],
                     "ubuntu": [10, 11],
                     }


def get_os_name():
    return platform.system().lower()


def get_platform_details():
    # system, node, release, version, machine, processor
    uname = platform.uname()

    return PlatformDetails(
            architecture=platform.architecture()[0],
            system=uname[0],
            hostname=uname[1],
            release=uname[2],
            machine=platform.machine(),
            processor=platform.processor(),
            )
