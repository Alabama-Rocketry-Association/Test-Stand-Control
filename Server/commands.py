'''Contains most commands that the user
can execute'''
from enum import Enum
import message as msg
import time
import os
import json

import board
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

import sensors

__author__ = "Aidan Cantu"

LAST_COMMAND = []

# load calibration data from JSON file
with open('settings.json') as f:
    settings = json.load(f)
    f.close()

# make JSON variables global variables in program
LOX_MOTOR_STEP_OFFSET = settings['motors']['lox_reg']['step_offset']
KER_MOTOR_STEP_OFFSET = settings['motors']['ker_reg']['step_offset']

# stepper1 --> M1, M2 terminals
# stepper2 --> M3, M4 terminals

# 200 steps --> 360 deg; 1.8 deg per step
# Gear ratio of 100:1

# stepper.FORWARD = clockwise, increase presssure
# stepper.BACKWARD = counterclockwise, decrease pressure

motors = MotorKit(i2c=board.I2C())
GEAR_RATIO = settings['motors']['lox_reg']['gear_ratio']
STEP_SIZE = settings['motors']['lox_reg']['step_size']

class Dev(Enum):
    LOX_MOTOR = 1
    KER_MOTOR = 2

def get_degrees(steps):
    global settings
    gear_ratio = settings['motors']['lox_reg']['gear_ratio']
    step_size = settings['motors']['lox_reg']['step_size'] 

    return steps*step_size/gear_ratio

def get_steps(degrees):
    global settings
    gear_ratio = settings['motors']['lox_reg']['gear_ratio']
    step_size = settings['motors']['lox_reg']['step_size']  

    return round(degrees*gear_ratio/step_size)

# Rotates specified motor by specified number of steps
def rotate_steps(motor, num_steps):
    global settings

    if num_steps > 0:
        dir = stepper.FORWARD
        inc = 1
    else:
        dir = stepper.BACKWARD
        inc = -1
        num_steps *= -1

    if motor == Dev.LOX_MOTOR:

        step_offset = settings['motors']['lox_reg']['step_offset']

        for i in range(num_steps):
            if msg.is_stopped():
                msg.tell("Stopping LOX_MOTOR at position %.2f degrees" % (get_degrees(step_offset)))
                break
            else:
                motors.stepper1.onestep(direction = dir, style=stepper.DOUBLE)
                step_offset += inc
                time.sleep(0.0001)
        motors.stepper1.release()

        # Update the JSON file with the new position
        settings['motors']['lox_reg']['step_offset'] = step_offset
        with open('settings.json', 'w') as f:
            f.write(json.dumps(settings))
            f.close()

        msg.tell("Successfully set LOX_MOTOR position to %.2f degrees" % (get_degrees(step_offset)))

    elif motor == Dev.KER_MOTOR:

        step_offset = settings['motors']['ker_reg']['step_offset']

        for i in range(num_steps):
            if msg.is_stopped():
                msg.tell("Stopping KER_MOTOR at position %.2f degrees" % (get_degrees(step_offset)))
                break
            else:
                motors.stepper2.onestep(direction = dir, style=stepper.DOUBLE)
                step_offset += inc
                time.sleep(0.0001)
        motors.stepper2.release()

        # Update the JSON file with the new position
        settings['motors']['ker_reg']['step_offset'] = step_offset
        with open('settings.json', 'w') as f:
            f.write(json.dumps(settings))
            f.close()

        msg.tell("Successfully set KER_MOTOR position to %.2f degrees" % (get_degrees(step_offset)))

def rotate(motor, amount_deg):

    if(abs(amount_deg) >= 90):
        user_message = "Type \'yes\' to confirm %s degrees on device %s" % (amount_deg, Dev(motor).name)
        if msg.demand(user_message) != 'yes':
            msg.tell("Operation Cancelled")
            return 4

    msg.tell(("Rotating %s Motor %s degrees") % (Dev(motor).name, amount_deg))
    msg.cmd_ready() 

    rotate_steps(motor, get_steps(amount_deg))

# input a psi value, and set the regulator to that specific psi value
def rotate_psi(motor, psi):
    global settings

    user_message = "Type \'yes\' to confirm %s psi on device %s" % (psi, Dev(motor).name)
    if msg.demand(user_message) != 'yes':
        msg.tell("Operation Cancelled")
        return 4

    #conversion array takes psi and gives location in degrees
    if motor == Dev.LOX_MOTOR:
        conversion = settings['motors']['lox_reg']['conversion']
        current_steps = settings['motors']['lox_reg']['step_offset']
    elif motor == Dev.KER_MOTOR:
        conversion = settings['motors']['ker_reg']['conversion']
        current_steps = settings['motors']['ker_reg']['step_offset']

    #find corresponding degree displacement
    new_pos = 0
    for i in range(len(conversion)):
        new_pos += (psi**i)*conversion[i]

    new_step_pos = get_steps(new_pos)

    msg.tell(("Rotating %s Motor %s degrees") % (Dev(motor).name, get_degrees(new_step_pos - current_steps)))
    msg.cmd_ready() 

    rotate_steps(motor, new_step_pos - current_steps)


#Rotates specified motor by specified number of steps
def lox_motor_pos():
    step_offset = settings['motors']['lox_reg']['step_offset']
    msg.tell("LOX Motor rotated %.2f degrees" % (get_degrees(step_offset)))

def ker_motor_pos():
    step_offset = settings['motors']['ker_reg']['step_offset']
    msg.tell("KEROSENE Motor rotated %.2f degrees" % (get_degrees(step_offset)))

def lox_psi(psi):
    rotate_psi(Dev.LOX_MOTOR, psi)

def ker_psi(psi):
    rotate_psi(Dev.KER_MOTOR, psi)

def lox_is():
    rotate(Dev.LOX_MOTOR,10)

def lox_ds():
    rotate(Dev.LOX_MOTOR,-10)

def ker_is():
    rotate(Dev.KER_MOTOR,10)

def ker_ds():
    rotate(Dev.KER_MOTOR,-10)

def lox_inc(n):
    rotate(Dev.LOX_MOTOR,n)

def lox_dec(n):
    rotate(Dev.LOX_MOTOR,-1*n)

def ker_inc(n):
    rotate(Dev.KER_MOTOR,n)

def ker_dec(n):
    rotate(Dev.KER_MOTOR,-1*n)

def help():
    s = '''
    lox_is: runs 10 degrees forward on lox
    lox_ds: runs 10 degrees backward on lox
    ker_is: runs 10 degrees forward on kerosene
    ker_ds: runs 10 degrees backward on kerosene

    lox_inc [n]: runs n degrees forward on lox
    lox_dec [n]: runs n degrees backward on lox
    ker_inc [n]: runs n degrees forward on kerosene
    ker_dec [n]: runs n degrees backward on kerosene

    lox_motor_pos: return angular offset of lox motor
    ker_motor_pos: return angular offset of ker motor

    lox_psi [n]: set the lox tank to n psi
    ker_psi [n]: psi: set the ker tank to n psi

    log [T/F]: start or stop logging sensor data
    calibrate: sets y-intercept of all sensors to 0

    ping: test connection
    help: print help menu
    rr: repeat last command
    reboot: restart server
    '''
    msg.tell(s)

# Starts or stops logging data from sensors
def log(currently_logging):
    if currently_logging.lower() == "true":
        msg.logging(True)
        msg.tell("Started Logging Data")
    elif currently_logging.lower() == "false":
        msg.logging(False)
        msg.tell("Stopped Logging Data")
    else:
        msg.tell("Error: Invalid Option (Enter \"True\" or \"False\")")

def calibrate():
    '''calibrates all sensors by setting the y-intercept
    of voltage-value conversion to 0'''
    sensors.calibrate_all()

# Repeats the previous command
def rr():
    if len(LAST_COMMAND) > 0:
        exe(LAST_COMMAND)
    else:
        return 1

def ping():
    msg.tell("pong")

def reboot():
    if msg.demand("Are you sure you want to reboot [yes/no]") == 'yes':
        msg.tell("Rebooting system (will automatically reconnect shortly)")
        os.system('sudo reboot now')
    else:
        msg.tell("aborting")

#dictionary of all commands, and number of args
commands = {
    "lox_is": [lox_is, 1],
    "lox_ds": [lox_ds, 1],
    "ker_is": [ker_is, 1],
    "ker_ds": [ker_ds, 1],

    "lox_inc": [lox_inc, 2],
    "lox_dec": [lox_dec, 2],
    "ker_inc": [ker_inc, 2],
    "ker_dec": [ker_dec, 2],

    "lox_motor_pos": [lox_motor_pos, 1],
    "ker_motor_pos": [ker_motor_pos, 1],

    "lox_psi": [lox_psi, 2],
    "ker_psi": [ker_psi, 2],

    "log": [log, 2],
    "calibrate": [calibrate, 1],

    "ping": [ping, 1],
    "help": [help, 1],
    "reboot": [reboot, 1],
    "rr": [rr, 1]
}

# Takes an array including command and arguments, and executes it
def exe(user_command):
    global LAST_COMMAND 

    user_method = user_command[0]
    user_args = user_command[1:]

    if user_method != 'rr':
        LAST_COMMAND = user_command


    if (user_method in commands.keys()) == False:
        msg.tell(("Error: command \"%s\" not found") % user_command )
        msg.cmd_ready()
        return 2
    
    method = commands.get(user_method)[0]
    num_args = commands.get(user_method)[1]

    if len(user_command) != num_args:
        msg.tell(("Error: %s arguments were given when %s were expected") % (len(user_command), num_args))
        msg.cmd_ready()
        return 3

    try:
        a = method(*user_args)
        msg.cmd_ready()
        return a
    except:
        msg.tell("An error has occured")
        msg.cmd_ready()
        return 1

# Converts a string to an array of arguments
def parse(user_input):
    user_input = str.lower(user_input)
    user_command = user_input.split()

    for i, item in enumerate(user_command):
        if item.isnumeric():
            user_command[i] = int(item)

    return user_command

