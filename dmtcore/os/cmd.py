SUDO = "sudo"

FDISK_LIST = ["fdisk", "-l"]

APPROVED_CMDS = [
   FDISK_LIST, 
]

for cmd in APPROVED_CMDS:
    cmd.insert(0, SUDO)
