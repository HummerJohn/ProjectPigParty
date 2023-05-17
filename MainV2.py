# List running python 
# ps -ef | grep python
# Encoder Video https://www.youtube.com/watch?v=vCaB5zJacrU
# Set up HTTP Server:
from server import ServerThread
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

# Reset Current_RPM to Zero
cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
sqliteConnection.commit()

# Setup Delay between pulses
PulsePerRotation = 1000 * 2 # 1000 comes from stepper driver
MicroSecondsPerPulse = int(((60/(0.1*10.0))/PulsePerRotation)*1000000)

# Initialize Direction Pin.
cursor.execute('SELECT Desired FROM Direction')
Desired_Dir = cursor.fetchone()[0]
if Desired_Dir == 1:
    GPIO.output(DirP,GPIO.HIGH)
else:
    GPIO.output(DirP,GPIO.LOW)

# Turn on power to USB - Turn on fans and Arduino
os.system('uhubctl -l 1-1 -p 2 -a 1')

# Wait for Arduino to be ready for serial communication
time.sleep(1)
# Setup Arduino
arduino = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=.1)
arduino.flush()

# SamplingTime = 1 # seconds
# Ramp = 0.1
RampRate = 0.2/1 # 0.1 per second
# Run until keyboard interupt
StartTime = time.time()
try:        
    while True:
        ElapsedTime = time.time() - StartTime
        if ElapsedTime > 1:
            StartTime = time.time()

            cursor.execute('SELECT Current FROM RPM')
            Current_RPM = cursor.fetchone()[0]
            cursor.execute('SELECT Desired FROM RPM')
            Desired_RPM = cursor.fetchone()[0]
            cursor.execute('SELECT Current FROM Direction')
            Current_Dir = cursor.fetchone()[0]    
            cursor.execute('SELECT Desired FROM Direction')
            Desired_Dir = cursor.fetchone()[0]

            if Current_Dir == Desired_Dir:
                # We don't want directional change so ramp to Desired RPM
                tmp_Desired_RPM = Desired_RPM 
            else:
                # We want directional change
                if Current_RPM == 0:
                    # If current RPM is 0 we can change direction
                    if Desired_Dir == 1:    
                        GPIO.output(DirP,GPIO.HIGH)
                    else:
                        GPIO.output(DirP,GPIO.LOW)
                    Current_Dir = Desired_Dir    
                    cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (Desired_Dir,1))
                    sqliteConnection.commit()
                else:
                    # Set Desired RPM to 0. let it ramp there. 
                    tmp_Desired_RPM = 0
            
            if Current_RPM != tmp_Desired_RPM:
                if abs(Current_RPM - tmp_Desired_RPM) < RampRate:
                    tmp_RampRate = abs(Current_RPM - tmp_Desired_RPM)
                else:
                    tmp_RampRate = RampRate

                if Current_RPM < tmp_Desired_RPM:
                    tmp_Desired_RPM = Current_RPM + tmp_RampRate
                else:
                    tmp_Desired_RPM = Current_RPM - tmp_RampRate
                

                if tmp_Desired_RPM < tmp_RampRate:
                    ToArduino = str(0) + "," + str(Current_Dir)
                    arduino.write(ToArduino.encode())
                    arduino.write(b'\n')
                    # Write 0 to Current_RPM
                    cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
                    sqliteConnection.commit()
                else:
                    # Set new speed to tmp_Desired_RPM
                    MicroSecondsPerPulse = int(((60/(tmp_Desired_RPM*10.0))/PulsePerRotation)*1000000)
                    print(str(MicroSecondsPerPulse) + " RPM: " + str(round(tmp_Desired_RPM,1)))
                    ToArduino = str(MicroSecondsPerPulse) + "," + str(Current_Dir)
                    arduino.write(ToArduino.encode())
                    arduino.write(b'\n')
                    cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (round(tmp_Desired_RPM,1),1))
                    sqliteConnection.commit()

        
        
        # print(arduino.readline().decode().strip())
        PositionInDegrees = arduino.readline().decode().strip()
        with server_thread.Position_lock:
            server_thread.Position = PositionInDegrees
        # print(PositionInDegrees)
        # cursor.execute("UPDATE Position SET Current = ? WHERE ID = ?", (PositionInDegrees,1))
        # sqliteConnection.commit()
        # time.sleep(max(0,1-ElapsedTime))

except KeyboardInterrupt:
    ToArduino = str(0) + "," + str(Current_Dir)
    arduino.write(ToArduino.encode())
    arduino.write(b'\n')
    sqliteConnection.close()
    server_thread.stop()
    server_thread.join()
    os.system('uhubctl -l 1-1 -p 2 -a 0')
    GPIO.cleanup()


