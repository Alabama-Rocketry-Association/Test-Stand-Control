'''List of methods which can read data from
various sensors on the assembly'''

from datetime import datetime
from enum import Enum
import threading

from ADCDifferentialPi import ADCDifferentialPi

__author__ = "Aidan Cantu"


# Global variable indicating if reading sensor data
SENSORS_AVAILABLE = threading.Event()
SENSORS_AVAILABLE.set()

# A/D Differential Sensor
ADC_ADDR_ONE = 0x68
ADC_ADDR_TWO = 0x6b
ADC_BITRATE = 14
ADC_GAIN = 8

adc = ADCDifferentialPi(ADC_ADDR_ONE, ADC_ADDR_TWO, ADC_BITRATE)
adc.set_pga(8)

class Data(Enum):
    LOX_PSI = 1
    KER_PSI = 2
    PRES_PSI = 3
    THRUST = 4

#Calibration for a + bx voltage/data translation
#First value is y-int, second is slope
conv_linear = {
    Data.LOX_PSI: [0.0006875, 10070],
    Data.KER_PSI: [0.0006875, 10070],
    Data.PRES_PSI: [0.0006875, 100700],
    Data.THRUST: [0, 5150000],

}

def read(data):
    '''Returns the specified data from the sensor'''
    voltage = read_voltage(data)
    convert = conv_linear.get(data)
    return convert[0] + voltage*convert[1]

def read_all():
    '''Collects data from all sensors and stores it as one
    line of a .csv file'''
    csv_string = datetime.now().strftime("%H:%M:%S.%f")[:-1]
    csv_string = csv_string + ','

    for item in Data:
        data_point = read(item)
        data_point = f'{data_point:.2f}'
        csv_string = csv_string + data_point + ','
    csv_string = csv_string[:-1] + "\n"
    
    return csv_string


def read_voltage(data):
    '''Returns the raw voltage value from the sensor'''
    global SENSORS_AVAILABLE, ADC_GAIN
    SENSORS_AVAILABLE.wait()
    SENSORS_AVAILABLE.clear()
    if data == Data.LOX_PSI:
        a =  adc.read_voltage(2)
    elif data == Data.KER_PSI:
        a = adc.read_voltage(4)
    elif data == Data.PRES_PSI:
        a = adc.read_voltage(3)
    elif data == Data.THRUST:
        a = adc.read_voltage(8)
    else:
        a = 0
    SENSORS_AVAILABLE.set()
    return a
    

def calibrate(data):
    '''sets current value from sensor as 0'''
    global conv_linear
    current_value = read(data)
    convert = conv_linear.get(data)
    conv_linear[data] = [convert[0] - current_value, convert[1]]           

def calibrate_all():
    '''calibrate all sensors'''
    for item in Data:
        calibrate(item)