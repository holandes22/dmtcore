from subprocess import check_output, STDOUT, CalledProcessError

SUDO = "sudo"
FDISK_LIST = ["fdisk", "-l"]

APPROVED_CMDS = [
   FDISK_LIST, 
]

for cmd in APPROVED_CMDS:
    cmd.insert(0, SUDO)

def run_cmd(cmd):
    if cmd not in APPROVED_CMDS:
        raise AttributeError
    try:
        #TODO: log INFO running cmd blah
        return check_output(cmd, stderr = STDOUT)
    except CalledProcessError:
        #TODO: log ERROR error and error.returncode
        raise

