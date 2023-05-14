# List running python 
# ps -ef | grep python


# Set up HTTP Server:
from server import run_server
import threading

server_thread = threading.Thread(target=run_server)
server_thread.start()


import sqlite3
import RPi.GPIO as GPIO
import serial
import time
import os

# Setup GPIO Pins
DirP = 3
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)    
GPIO.setup(DirP,GPIO.OUT)

# Open connection to SQLite Database
sqliteConnection = sqlite3.connect('my_database.db')
cursor = sqliteConnection.cursor()

# Check Stepper Driver.
PulsePerRotation = 1000 * 2

# Get the L
# cursor.execute('SELECT Current FROM RPM')
# Current_RPM = cursor.fetchone()[0]
# if Current_RPM == 0:

# Always start at very low RPM
Current_RPM = 0.1
cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
Desired_RPM = 0
SecondsPerRotation = 60/(Current_RPM*10.0)
SecondsPerPulse = SecondsPerRotation/PulsePerRotation
MiliSecondsPerPulse = SecondsPerPulse * 1000
# Initialize Direction Pin.
GPIO.output(DirP,GPIO.HIGH)

# Turn on power to USB - Turn on fans
os.system('uhubctl -l 1-1 -p 2 -a 1')
time.sleep(5)
# Setup Arduino
arduino = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=.1)

# Run until keyboard interupt
try:        
    while True:
        cursor.execute('SELECT Current FROM RPM')
        Current_RPM = cursor.fetchone()[0]
        cursor.execute('SELECT Desired FROM RPM')
        Desired_RPM = cursor.fetchone()[0]

        if Desired_RPM != Current_RPM:
            if Desired_RPM != 0:
                print("Received Desired RPM: ", Desired_RPM)
                SecondsPerRotation = 60/(Desired_RPM*10.0)
                SecondsPerPulse = SecondsPerRotation/PulsePerRotation # Delay between each Pulse
                MiliSecondsPerPulse = int(SecondsPerPulse * 1000000)
                print("Sending MiliSecondsPerPulse to Arduino: ", MiliSecondsPerPulse)
                print(str(MiliSecondsPerPulse))
                arduino.write(bytes(str(MiliSecondsPerPulse), 'utf-8'))
            else:
                # Send 0 to Arduino
                arduino.write(bytes(str(0), 'utf-8'))
            cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (Desired_RPM,1))
            sqliteConnection.commit()
        time.sleep(1)

except KeyboardInterrupt:
    sqliteConnection.close()
    os.system('uhubctl -l 1-1 -p 2 -a 0')
    GPIO.cleanup()
    
# # subprocess.run([python],)

# import sqlite3

# sqliteConnection = sqlite3.connect('my_database.db')
# cursor = sqliteConnection.cursor()
# cursor.execute('DROP TABLE RPM')
# cursor.execute('CREATE TABLE Desired_RPM VALUES ())
# cursor.execute('CREATE TABLE RPM (ID INT, Desired REAL, Current REAL)')
# cursor.execute("INSERT INTO RPM (Current) VALUES (?)", (3.0,))
# cursor.execute("INSERT INTO RPM (ID) VALUES (?)", (1,))
# cursor.execute('SELECT Current FROM RPM')
# current_value = cursor.fetchone()[0]
# print(current_value)

# cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (3.0,1))

# cursor.execute('DROP TABLE RPM')
# sqliteConnection.commit()
# sqliteConnection.close()


