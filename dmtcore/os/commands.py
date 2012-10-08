import os
import logging
from subprocess import check_output, STDOUT, CalledProcessError

module_logger = logging.getLogger("dmtcore.os.commands")

#List of approved commands
SIZE_FROM_FDISK = ['/sbin/fdisk', '-l']
BLKID = ['/sbin/blkid', '-o', 'export']
MULTIPATH_LIST = ['/sbin/multipath',  '-ll']

APPROVED_CMDS = [
                 SIZE_FROM_FDISK,
                 BLKID,
                 MULTIPATH_LIST,
                 ]

def run_cmd(cmd, run_as_sudo=True):
    try:
        if run_as_sudo or os.geteuid() != 0:
            cmd.insert(0, "sudo")
        module_logger.info("Running command {0}".format(cmd))
        return check_output(cmd, stderr=STDOUT)
    except CalledProcessError as e:
        module_logger.error("Error while running command {0}.Output: {1}.\
                                Return code: {2}".format(cmd, e.output, e.returncode))
        raise
