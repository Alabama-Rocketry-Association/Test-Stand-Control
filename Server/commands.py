'''Contains most commands that the user
can execute'''
from enum import Enum
import message as msg
import time
import os
import json

import RPi.GPIO as GPIO
import board
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

import sensors

__author__ = "Aidan Cantu"

LAST_COMMAND = []

# load data from JSON file
with open('settings.json') as f:
    settings = json.load(f)
    f.close()

# initialize GPIO
def init_gpio():
    global settings


    for key in settings['gpio']:
        
        dev = settings['gpio'][key]

        if dev['mode']=='out':
            GPIO.setup(dev['gpio'], GPIO.OUT)
            GPIO.output(dev['gpio'], dev['default'])
            
        elif dev['mode']=='in':
            GPIO.setup(dev['gpio'], GPIO.IN)
            GPIO.output(dev[key]['gpio'], dev['default'])

        elif dev['mode']=='opendrain':
            if dev['default'] == 1:
                 GPIO.setup(dev['gpio'], GPIO.OUT)
                 GPIO.output(dev['gpio'], 0)
            elif dev['default'] == 0:
                GPIO.setup(dev['gpio'], GPIO.IN)
        
    return 0

GPIO.cleanup()
GPIO.setmode(GPIO.BCM) 
init_gpio()

motors = MotorKit(i2c=board.I2C())

# stepper1 --> M1, M2 terminals
# stepper2 --> M3, M4 terminals

# 200 steps --> 360 deg; 1.8 deg per step
# Gear ratio of 100:1

# stepper.FORWARD = clockwise, increase presssure
# stepper.BACKWARD = counterclockwise, decrease pressure

class Dev(Enum):
    LOX_MOTOR = 1
    KER_MOTOR = 2

# Set the GPIO pin item to the specified value
def set_gpio(item, value):
    global settings
    for key in settings['gpio']:
        dev = settings['gpio'][key]
        if key==item and dev['mode'] == "out":
            GPIO.output(dev['gpio'], value)
            dev['current'] = value
            save()
            return 0
        elif key==item and dev['mode'] == "opendrain":
            if value == 1:
                GPIO.setup(dev['gpio'], GPIO.OUT) 
            elif value == 0:
                GPIO.setup(dev['gpio'], GPIO.IN)

            save()
            return 0
    return 1

# Open the corresponding valve by setting the GPIO to low
def open_valve(valve):
    if set_gpio(valve, 1) == 0:
        msg.tell("Opened %s" % valve)
        return 0
    msg.tell("%s does not exist, operation cancelled" % valve)
    return 0

# Close the corresponding valve by setting the GPIO to high
def close_valve(valve):
    if set_gpio(valve, 0) == 0:
        msg.tell("Closed %s" % valve)
        return 0
    msg.tell("%s does not exist, operation cancelled" % valve)
    return 0

# Enable the 2ways or the ignitor
def enable(item):
    if item=='2way' or item=='twoway':
        open_valve('press_2way')
        open_valve('ventlox_2way')
        open_valve('ventker_2way')
        open_valve('mainlox_2way')
        open_valve('mainker_2way')
        return 0
    elif item=='ignition' or item=='ignitor' or item=='igniter':
        open_valve('ignition')
        return 0
    msg.tell("%s does not exist, operation cancelled" % item)
    return 0

# Disable the 2ways or the ignitor
def disable(item):
    if item=='2way' or item=='twoway':
        close_valve('press_2way')
        close_valve('ventlox_2way')
        close_valve('ventker_2way')
        close_valve('mainlox_2way')
        close_valve('mainker_2way')
        return 0
    elif item=='ignition' or item=='ignitor' or item=='igniter':
        close_valve('ignition')
        return 0
    msg.tell("%s does not exist, operation cancelled" % item)
    return 0

# Convert a number of steps on the motor to the number of corresponding degrees
def get_degrees(steps):
    global settings
    gear_ratio = settings['lox_reg']['gear_ratio']
    step_size = settings['lox_reg']['step_size'] 

    return steps*step_size/gear_ratio

# Convert a number of degrees to the approximate number of corresponding steps
def get_steps(degrees):
    global settings
    gear_ratio = settings['lox_reg']['gear_ratio']
    step_size = settings['lox_reg']['step_size']  

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

    # Rotate the LOX_MOTOR
    if motor == Dev.LOX_MOTOR:
        step_offset = settings['lox_reg']['step_offset']

        for i in range(num_steps):
            if msg.is_stopped():
                msg.tell("Stopping LOX_MOTOR at position %.2f degrees" % (get_degrees(step_offset)))
                break
            else:
                motors.stepper1.onestep(direction = dir, style=stepper.DOUBLE)
                step_offset += inc
                settings['lox_reg']['step_offset'] = step_offset
                time.sleep(0.0001)
        motors.stepper1.release()

        msg.tell("Successfully set LOX_MOTOR position to %.2f degrees" % (get_degrees(step_offset)))

    # Rotate the KER_MOTOR
    elif motor == Dev.KER_MOTOR:
        step_offset = settings['ker_reg']['step_offset']

        for i in range(num_steps):
            if msg.is_stopped():
                msg.tell("Stopping KER_MOTOR at position %.2f degrees" % (get_degrees(step_offset)))
                break
            else:
                motors.stepper2.onestep(direction = dir, style=stepper.DOUBLE)
                step_offset += inc
                settings['ker_reg']['step_offset'] = step_offset
                time.sleep(0.0001)
        motors.stepper2.release()

        msg.tell("Successfully set KER_MOTOR position to %.2f degrees" % (get_degrees(step_offset)))

    # Update the JSON file with the new position
    save()

# rotate the specified motor by a specified number of degrees
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
        conversion = settings['lox_reg']['conversion']
        current_steps = settings['lox_reg']['step_offset']
    elif motor == Dev.KER_MOTOR:
        conversion = settings['ker_reg']['conversion']
        current_steps = settings['ker_reg']['step_offset']

    #find corresponding degree displacement
    new_pos = 0
    for i in range(len(conversion)):
        new_pos += (psi**i)*conversion[i]

    new_step_pos = get_steps(new_pos)

    msg.tell(("Rotating %s Motor %s degrees") % (Dev(motor).name, get_degrees(new_step_pos - current_steps)))
    msg.cmd_ready() 

    rotate_steps(motor, new_step_pos - current_steps)


# Get the current angular displacement of each motor
def lox_motor_pos():
    step_offset = settings['lox_reg']['step_offset']
    msg.tell("LOX Motor rotated %.2f degrees" % (get_degrees(step_offset)))

def ker_motor_pos():
    step_offset = settings['ker_reg']['step_offset']
    msg.tell("KEROSENE Motor rotated %.2f degrees" % (get_degrees(step_offset)))

# Set each motor to the approximate PSI level
def lox_psi(psi):
    rotate_psi(Dev.LOX_MOTOR, psi)

def ker_psi(psi):
    rotate_psi(Dev.KER_MOTOR, psi)

# Rotate each motor by n degrees
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
    lox_inc [n]: runs n degrees forward on lox
    lox_dec [n]: runs n degrees backward on lox
    ker_inc [n]: runs n degrees forward on kerosene
    ker_dec [n]: runs n degrees backward on kerosene

    lox_psi [n]: set the lox tank to n psi
    ker_psi [n]: psi: set the ker tank to n psi 

    open [valve]: opens the corresponding valve
    close [valve]: closes the corresponding valve

    enable [item]: enables the corresponding item
    disable [item]: disables the corresponding item

    lox_motor_pos: return angular offset of lox motor
    ker_motor_pos: return angular offset of ker motor

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

    "lox_inc": [lox_inc, 2],
    "lox_dec": [lox_dec, 2],
    "ker_inc": [ker_inc, 2],
    "ker_dec": [ker_dec, 2],

    "lox_psi": [lox_psi, 2],
    "ker_psi": [ker_psi, 2],

    "open": [open_valve, 2],
    "close": [close_valve, 2],

    "enable": [enable, 2],
    "disable": [disable, 2],

    "lox_motor_pos": [lox_motor_pos, 1],
    "ker_motor_pos": [ker_motor_pos, 1],

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
    except Exception as e:
        msg.tell("An error has occured:")
        msg.tell(str(e))
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

# Save current settings dictionary to file
def save():
    global settings
    with open('settings.json', 'w') as f:        
        f.write(json.dumps(settings), indent=4)
        f.close()
