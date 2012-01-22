import os
from collections import namedtuple

def get_major_minor(device_filepath):
    stat = os.stat(device_filepath)
    MajorMinor = namedtuple('MajorMinor', 'major,minor')
    return MajorMinor(os.major(stat.st_rdev), os.minor(stat.st_rdev))