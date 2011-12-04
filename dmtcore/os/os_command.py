from subprocess import check_output, STDOUT, CalledProcessError

def os_command(cmd):
    try:
        return check_output(cmd, stderr = STDOUT)
    except CalledProcessError:
        #log error and error.returncode
        raise
        
        
        
        
