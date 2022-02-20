import math
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from data_handler import data_handler
from class_making import *
import numpy
import pandas as pd
import numpy as np
import sys
from time import sleep
import csv
global data_read
sec_total = 0
csv_file = ''  # Keep this as an empty string
data_read = ''

# Deciding whether to 

while True:
  try:
    time_increment = int(input("Input GUI update speed (in ms): "))
    if time_increment <= 50:
        print("Please input integer above 50 only...") 
        continue 
    break
  except ValueError:
      print("Please input integer above 50 only...")  
      continue

import_host = input('Are you attached to the pi? (y/n): ')

if import_host == 'y':
    import host
    csv_file = host.get_file_name()
    with open(csv_file, 'a', newline='') as my_csv_file:
        csv_writter = csv.writer(my_csv_file)
        csv_writter.writerow([0,1,2,3])
    data_read = 'CSV'

else:
    desired_data = input('Enter "csv" to read from csv, enter any entry to switch to dummy data: ')
        
    if desired_data == 'csv' or desired_data == 'CSV':
        csv_file = input('Please enter the name of the csv file: ')
        try:
            f = open(csv_file, 'rb')
        except OSError:
            print("Could not open/read file:", csv_file)
            sys.exit()
        data_read = 'CSV'
        print("CSV mode activated.")
    else:
        data_read = 'Dummy'
        print("Dummy mode activated.")



def update_graphs(sensors):  # This accepts a dictionary of sensors (created in the initialization area)
    for sensor in sensors.values():
        sensor.graph_update(sec_total)
    # return data_combined


# A function used to update the GUI - choose what data you want updated
def update():
    global sec_total
    global time_increment
    try:
        sec_total += (time_increment / 1000)
        update_time(sec_total, time_increment)  # Include this to update the global time + graph with time increments
        update_graphs(p_sensors1)  # To add graph functionality, do this command, and feed the sensor array dictionary
        update_graphs(p_sensors2)
        update_graphs(p_sensors3)
        #update_graphs(t_sensors)

    except IndexError:
        print('Something is not indexing in the update function in main.py, please fix')


'''
    Initialization code -------------------------------------------------------------
'''

# time_increment = 100  # Amount of time it will take to update the GUI and data collection, measured in ms

# declare object for serial Communication
# ser = Communication()
# declare object for storage in CSV
# data_base = data_handler()

# Example pressure sensor objects and characteristics
p_sensors1 = {
    'p_sensor1': Sensor('Pressurant P Sensor 1', 'Pressure', 1, 2, csv_file, data_read, time_increment),
    # 'p_sensor2': Sensor('Pressure Sensor 2', 'Pressure', 1, 1, csv_file, data_read, time_increment),
    # 'p_sensor3': Sensor('Pressure Sensor 3', 'Pressure', 1, 2, csv_file, data_read, time_increment)
}
# Creating a second pressure sensor array
p_sensors2 = {
    'p_sensor4': Sensor('Fuel P Sensor 1', 'Pressure', 2, 1, csv_file, data_read, time_increment),
    # 'p_sensor5': Sensor('Pressure Sensor 5', 'Pressure', 2, 4, csv_file, data_read, time_increment),
    # 'p_sensor6': Sensor('Pressure Sensor 6', 'Pressure', 2, 5, csv_file, data_read, time_increment)
}
# Creating a third pressure sensor array
p_sensors3 = {
    'p_sensor7': Sensor('LOX P Sensor 1', 'Pressure', 3, 0, csv_file, data_read, time_increment),
    # 'p_sensor8': Sensor('Pressure Sensor 8', 'Pressure', 3, 7, csv_file, data_read, time_increment),
    # 'p_sensor9': Sensor('Pressure Sensor 9', 'Pressure', 3, 8, csv_file, data_read, time_increment)
}
# Example temperature sensor objects and characteristics
'''
t_sensors = {
    't_sensor1': Sensor('Temperature Sensor 1', 'Temperature', 4, 0, csv_file, data_read, time_increment),
    't_sensor2': Sensor('Temperature Sensor 2', 'Temperature', 4, 1, csv_file, data_read, time_increment),
    't_sensor3': Sensor('Temperature Sensor 3', 'Temperature', 4, 2, csv_file, data_read, time_increment)
}
'''



'''
    GUI Set-up and Updating Scripts ========================================================================
'''

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(time_increment)  # Set this to the desired update speed of the GUI [milliseconds]

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
