import platform
from collections import namedtuple


PlatformDetails = namedtuple("PlatformDetails", "architecture,machine,processor,system,version")
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
    return PlatformDetails(
            architecture=platform.architecture(),
            machine=platform.machine(),
            processor=platform.processor(),
            system=platform.system(),
            version=platform.version()
            )
