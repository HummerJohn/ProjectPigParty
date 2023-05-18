# List running python 
# ps -ef | grep python

# Set up HTTP Server:
from HTTPServer.server import ServerThread
# import threading

# server_thread = threading.Thread(target=run_server)
server_thread = ServerThread()

with server_thread.Position_lock:
    server_thread.Position = 0
    
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

# Always start at very low RPM
Current_RPM = 0.1
cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
sqliteConnection.commit()
Desired_RPM = 0
# Check Stepper Driver.
PulsePerRotation = 1000 * 2
MicroSecondsPerPulse = int(((60/(Current_RPM*10.0))/PulsePerRotation)*1000000)

# Initialize Direction Pin.
cursor.execute('SELECT Desired FROM Direction')
Desired_Dir = cursor.fetchone()[0]
Current_Dir = Desired_Dir
if Desired_Dir == 1:
    GPIO.output(DirP,GPIO.HIGH)
else:
    GPIO.output(DirP,GPIO.LOW)

# Turn on power to USB - Turn on fans
os.system('uhubctl -l 1-1 -p 2 -a 1')

time.sleep(1)
# Setup Arduino
arduino = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=.1)
arduino.flush()
# Run until keyboard interupt
try:        
    while True:
        if Desired_RPM != Current_RPM:
            if Desired_RPM != 0:
                print("Received Desired RPM: ", Desired_RPM)
                MicroSecondsPerPulse = int(((60/(Desired_RPM*10.0))/PulsePerRotation)*1000000)
                print("Sending MicroSecondsPerPulse to Arduino: ", MicroSecondsPerPulse)

                arduino.write(str(MicroSecondsPerPulse).encode())
                arduino.write(b'\n')
                # Current_PPS = int(arduino.readline().decode().strip())
                # print("Arduino Feedback: " + str(Current_RPM))
            else:
# Missing Ramp to 0  
                # Send 0 to Arduino
                arduino.write(str(0).encode())
                arduino.write(b'\n')
            cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (Desired_RPM,1))
            sqliteConnection.commit()
        if Desired_Dir != Current_Dir:
            if Desired_Dir == 1:
                GPIO.output(DirP,GPIO.HIGH)
                print("Running CounterClockwise")
            else:   
                print("Running Clockwise")
                GPIO.output(DirP,GPIO.LOW)
            cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (Desired_Dir,1))
            sqliteConnection.commit()   
    
        cursor.execute('SELECT Current FROM RPM')
        Current_RPM = cursor.fetchone()[0]
        cursor.execute('SELECT Desired FROM RPM')
        Desired_RPM = cursor.fetchone()[0]
        cursor.execute('SELECT Current FROM Direction')
        Current_Dir = cursor.fetchone()[0]    
        cursor.execute('SELECT Desired FROM Direction')
        Desired_Dir = cursor.fetchone()[0]

        time.sleep(1)

except KeyboardInterrupt:
    arduino.write(str(0).encode())
    arduino.write(b'\n')
    sqliteConnection.close()
    server_thread.stop()
    server_thread.join()
    os.system('uhubctl -l 1-1 -p 2 -a 0')
    GPIO.cleanup()


