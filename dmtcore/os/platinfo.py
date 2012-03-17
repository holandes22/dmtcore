import platform


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