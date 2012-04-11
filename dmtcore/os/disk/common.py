import os
from collections import namedtuple

MajorMinor = namedtuple('MajorMinor', 'major,minor')


def get_major_minor(device_filepath):
    stat = os.stat(device_filepath)
    return MajorMinor(major = os.major(stat.st_rdev), minor = os.minor(stat.st_rdev))
