from subprocess import check_output, STDOUT, CalledProcessError

#List of approved commands

SIZE_FROM_FDISK = ['/sbin/fdisk', '-l']

APPROVED_CMDS = [
                 SIZE_FROM_FDISK,
                 ]

def run_cmd(cmd, run_as_sudo = True):
    #For dynamic cmds, usually the last arg is the one added dinamically
    #TODO: Find a better wat to deal with this: issue 6
    if cmd[:-1] in APPROVED_CMDS or cmd in APPROVED_CMDS:
        try:
            if run_as_sudo:
                cmd.insert(0, "sudo")
            #TODO: log INFO running cmd blah
            return check_output(cmd, stderr = STDOUT)
        except CalledProcessError:
            #TODO: log ERROR error and error.returncode
            raise
    else:
        #TODO: Raise a more meaningful error
        raise AttributeError

