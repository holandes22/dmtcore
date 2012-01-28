from subprocess import check_output, STDOUT, CalledProcessError

#List of approved commands

from dmtcore.os.disk.linux import SIZE_FROM_FDISK

SUDO = "sudo"

APPROVED_CMDS = [
   SIZE_FROM_FDISK
]

for cmd in APPROVED_CMDS:
    cmd.insert(0, SUDO)

def run_cmd(cmd):
    #For dynamic cmds, usually the last arg is the one added dinamically
    #TODO: Find a better wat to deal with this: issue 6
    if cmd not in APPROVED_CMDS or cmd[:-1] not in APPROVED_CMDS:
        #TODO: Raise a more meaningful error
        raise AttributeError
    try:
        #TODO: log INFO running cmd blah
        return check_output(cmd, stderr = STDOUT)
    except CalledProcessError:
        #TODO: log ERROR error and error.returncode
        raise

