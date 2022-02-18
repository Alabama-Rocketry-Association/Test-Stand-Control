import math
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from data_handler import data_handler
# from GUI import *
from class_making import *
import numpy
import pandas as pd
import numpy as np
import sys
from time import sleep
import csv
import host
global data_read
sec_total = 0


def update_graphs(sensors):  # This accepts a dictionary of sensors (created in the initialization area)
    for sensor in sensors.values():
        sensor.graph_update(sec_total)
    # return data_combined


# A function used to update the GUI - choose what data you want updated
def update():
    global sec_total
    try:
        sec_total += (time_increment / 1000)
        update_time(sec_total, time_increment)  # Include this to update the global time + graph with time increments
        update_graphs(p_sensors1)  # To add graph functionality, do this command, and feed the sensor array dictionary
        update_graphs(p_sensors2)
        update_graphs(p_sensors3)
        #update_graphs(t_sensors)

        # data_base.save(value_chain) # Part of the saving function, needs to be reworked

    except IndexError:
        print('Something is not indexing in the update function in main.py, please fix')


'''
    Initialization code -------------------------------------------------------------
'''
# press_csv = 'data_example.csv'  # The csv file to read things in from
csv_file = ''
read_csv = False  # If reading in live data from csv, set this to true
time_increment = 250  # Amount of time it will take to update the GUI and data collection, measured in ms

# declare object for serial Communication
ser = Communication()
# declare object for storage in CSV
data_base = data_handler()

# Begins the loop/ update for the GUI script
if ser.isOpen() or ser.dummyMode() or ser.csvMode():
    if ser.isOpen():
        data_read = "Serial"
    elif ser.dummyMode():
        data_read = "Dummy"
    elif ser.csvMode():
        data_read = "CSV"
        csv_file = host.get_file_name()
        try:
            f = open(csv_file, 'rb')
        except OSError:
            print("Could not open/read file:", csv_file)
            sys.exit()

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(time_increment)  # Set this to the desired update speed of the GUI [milliseconds]
else:
    print("Something is wrong with the update call for the GUI, investigate!")


# Example pressure sensor objects and characteristics
p_sensors1 = {
    'p_sensor1': Sensor('Pressure Sensor 1', 'Pressure', 1, 0, csv_file, data_read),
    # 'p_sensor2': Sensor('Pressure Sensor 2', 'Pressure', 1, 1, csv_file, data_read),
    # 'p_sensor3': Sensor('Pressure Sensor 3', 'Pressure', 1, 2, csv_file, data_read)
}
# Creating a second pressure sensor array
p_sensors2 = {
    'p_sensor4': Sensor('Pressure Sensor 4', 'Pressure', 2, 1, csv_file, data_read),
    #'p_sensor5': Sensor('Pressure Sensor 5', 'Pressure', 2, 4, csv_file, data_read),
    #'p_sensor6': Sensor('Pressure Sensor 6', 'Pressure', 2, 5, csv_file, data_read)
}
# Creating a third pressure sensor array
p_sensors3 = {
    'p_sensor7': Sensor('Pressure Sensor 7', 'Pressure', 3, 2, csv_file, data_read),
    #'p_sensor8': Sensor('Pressure Sensor 8', 'Pressure', 3, 7, csv_file, data_read),
    #'p_sensor9': Sensor('Pressure Sensor 9', 'Pressure', 3, 8, csv_file, data_read)
}
# Example temperature sensor objects and characteristics
'''
t_sensors = {
    't_sensor1': Sensor('Temperature Sensor 1', 'Temperature', 4, 0, csv_file, data_read),
    't_sensor2': Sensor('Temperature Sensor 2', 'Temperature', 4, 1, csv_file, data_read),
    't_sensor3': Sensor('Temperature Sensor 3', 'Temperature', 4, 2, csv_file, data_read)
}
'''



'''
    GUI Set-up and Updating Scripts ========================================================================
'''


# This is the command that keeps the GUI file running
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()  # This command (.exec) runs the program and opens everything above


'''
    Stuff that is going to run if/when you click the 'x' to exit the GUI ======================================
'''


'''# Infinite loop will not run until GUI is closed - decide if anything needs to happen after GUI closes
while True:
    print('Test test test')
    sleep(1)'''
