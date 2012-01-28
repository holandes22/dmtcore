import logging
from subprocess import check_output, STDOUT, CalledProcessError

module_logger = logging.getLogger("dmtcore.os.commands")

#List of approved commands
SIZE_FROM_FDISK = ['/sbin/fdisk', '-l']

APPROVED_CMDS = [
                 SIZE_FROM_FDISK,
                 ]

module_logger.info("List of Approved commands: %s" % APPROVED_CMDS)

def run_cmd(cmd, run_as_sudo = True):
    #For dynamic cmds, usually the last arg is the one added dinamically
    #TODO: Find a better wat to deal with this: issue 6
    if cmd[:-1] in APPROVED_CMDS or cmd in APPROVED_CMDS:
        try:
            if run_as_sudo:
                cmd.insert(0, "sudo")
            #TODO: log INFO running cmd blah
            module_logger.info("Running command {0}".format(cmd))
            return check_output(cmd, stderr = STDOUT)
        except CalledProcessError as e:
            #TODO: log ERROR error and error.returncode
            module_logger.error("Error caught while running command {0}. {1}".format(cmd, e))
            raise
    else:
        #TODO: Raise a more meaningful error
        module_logger.error("Running command {0} is not allowed. Verify it belongs to the approved commands list.".format(cmd))
        raise AttributeError

