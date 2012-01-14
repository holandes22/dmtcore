import os

def get_major_minor(device_filepath):
    stat = os.stat(device_filepath)
    return (os.major(stat.st_rdev), os.minor(stat.st_rdev))