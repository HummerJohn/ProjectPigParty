# List running python 
# ps -ef | grep python
import sqlite3
import serial
import time
import os
from HTTPServer.server import ServerThread

# Set up HTTP Server:
server_thread = ServerThread()
with server_thread.Position_lock:
    server_thread.Position = 0
server_thread.start()

# Open connection to SQLite Database
sqliteConnection = sqlite3.connect('my_database.db')
cursor = sqliteConnection.cursor()

# Reset Current_RPM to Zero
cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
sqliteConnection.commit()

# Setup Delay between pulses
PulsePerRotation = 1000 * 2 # 1000 comes from stepper driver
MicroSecondsPerPulse = int(((60/(0.1*10.0))/PulsePerRotation)*1000000)

# Read initial direction
cursor.execute('SELECT Desired FROM Direction')
Desired_Dir = cursor.fetchone()[0]
# Write it to current Direction
cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (Desired_Dir,1))
sqliteConnection.commit()

# Turn on power to USB - Turn on fans and Arduino

# Wait for Arduino to be ready for serial communication
time.sleep(1)
# Setup Arduino
arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
arduino.flush()

SamplingTime = 1 # For Arduino Control
RampRate = 0.2/(1/SamplingTime) # 0.2 per second

# Setup default msg and send it.
msg_Delay = str(0)
msg_Direction = "," + str(Desired_Dir)
msg_ResetPosition =  "," + str(1) 
arduino.write((msg_Delay+msg_Direction+msg_ResetPosition).encode())
arduino.write(b'\n')

StartTime = time.time()
# Run until keyboard interupt
try:        
    while True:
        ElapsedTime = time.time() - StartTime
        if ElapsedTime > SamplingTime:
            StartTime = time.time()

            # Read Needed information from DB
            cursor.execute('SELECT Current FROM RPM')
            Current_RPM = cursor.fetchone()[0]
            cursor.execute('SELECT Desired FROM RPM')
            Desired_RPM = cursor.fetchone()[0]
            cursor.execute('SELECT Current FROM Direction')
            Current_Dir = cursor.fetchone()[0]    
            cursor.execute('SELECT Desired FROM Direction')
            Desired_Dir = cursor.fetchone()[0]
            cursor.execute('SELECT Desired FROM Position')
            Desired_Pos = cursor.fetchone()[0]
            
            if Desired_Pos == 0:
                # Reset Position button was pressed.
                msg_ResetPosition =  "," + str(0)
                arduino.write((msg_Delay+msg_Direction+msg_ResetPosition).encode())
                arduino.write(b'\n')
                msg_ResetPosition =  "," + str(1)
                cursor.execute("UPDATE Position SET Desired = ? WHERE ID = ?", (1,1))
                sqliteConnection.commit() 
            
            if Current_Dir == Desired_Dir:
                # We don't want directional change so ramp to Desired RPM
                tmp_Desired_RPM = Desired_RPM 
            else:
                # We want directional change
                if Current_RPM == 0:
                    # The speed is zero so we change direction and write it to DB
                    Current_Dir = Desired_Dir    
                    cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (Desired_Dir,1))
                    sqliteConnection.commit()
                else:
                    # We are rotating so we have to ramp down before changing direction 
                    tmp_Desired_RPM = 0
            
            if Current_RPM != tmp_Desired_RPM:
                # We have to change the speed we are rotating at
                if abs(Current_RPM - tmp_Desired_RPM) < RampRate:
                    # handling no overshoot/undershoot
                    tmp_RampRate = abs(Current_RPM - tmp_Desired_RPM)
                else:
                    tmp_RampRate = RampRate

                if Current_RPM < tmp_Desired_RPM:
                    # Envoking ramprate instead of just jumping to new speed.
                    tmp_Desired_RPM = Current_RPM + tmp_RampRate
                else:
                    tmp_Desired_RPM = Current_RPM - tmp_RampRate
                

                if tmp_Desired_RPM < tmp_RampRate:
                    # In this case we have a desired speed close to zero or a zero, so we overwrite with 0 speed
                    msg_Delay = str(0)
                    msg_Direction = "," + str(Current_Dir)
                    arduino.write((msg_Delay+msg_Direction+msg_ResetPosition).encode())
                    arduino.write(b'\n')
                    cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
                    sqliteConnection.commit()
                else:
                    # Set new speed to tmp_Desired_RPM
                    # Compute delay
                    MicroSecondsPerPulse = int(((60/(tmp_Desired_RPM*10.0))/PulsePerRotation)*1000000)
                    print(str(MicroSecondsPerPulse) + " RPM: " + str(round(tmp_Desired_RPM,1)))
                    msg_Delay = str(MicroSecondsPerPulse)
                    msg_Direction = "," + str(Current_Dir)
                    arduino.write((msg_Delay+msg_Direction+msg_ResetPosition).encode())
                    arduino.write(b'\n')
                    cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (round(tmp_Desired_RPM,1),1))
                    sqliteConnection.commit()

        # Read Position from arduino insert into the shared variable.
        PositionInDegrees = arduino.readline().decode().strip()
        with server_thread.Position_lock:
            server_thread.Position = PositionInDegrees

except KeyboardInterrupt:
    # Shut down "gracefully"
    ToArduino = str(0) + "," + str(Current_Dir)
    arduino.write((ToArduino+msg_ResetPosition).encode())
    arduino.write(b'\n')
    sqliteConnection.close()
    server_thread.stop()
    server_thread.join()


