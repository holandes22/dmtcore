import os
from collections import namedtuple

MajorMinor = namedtuple('MajorMinor', 'major,minor')

def get_major_minor(device_filepath):
    stat = os.stat(device_filepath)
    return MajorMinor(os.major(stat.st_rdev), os.minor(stat.st_rdev))