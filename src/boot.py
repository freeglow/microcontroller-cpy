import board
import digitalio
import storage

'''
By default, file system is read-only when connected to a computer. This
is to allow the device to read/write to itself when in normal operation.

To enable write access (thereby disabling write access for the board iteself):
- Push the onboard reset switch
- Hold the user switch while rebooting
'''
def setStorageAccess():
    switch = digitalio.DigitalInOut(board.SWITCH)
        
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.UP
        
    # If the switch pin is connected to ground CircuitPython can write to the drive
    storage.remount("/", switch.value)

setStorageAccess()