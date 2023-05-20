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
sqlite_connection = sqlite3.connect('my_database.db')
cursor = sqlite_connection.cursor()

# Reset current_rpm to Zero
cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
sqlite_connection.commit()

# Setup Delay between pulses
PULSE_PER_ROTATION = 1000 * 2 # 1000 comes from stepper driver
micro_seconds_per_pulse = int(((60/(0.1*10.0))/PULSE_PER_ROTATION)*1000000)

# Read initial direction
cursor.execute('SELECT Desired FROM Direction')
desired_dir = cursor.fetchone()[0]
# Write it to current Direction
cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (desired_dir,1))
sqlite_connection.commit()

# Turn on power to USB - Turn on fans and Arduino

# Wait for Arduino to be ready for serial communication
time.sleep(1)
# Setup Arduino
arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
arduino.flush()

SAMPLING_TIME = 1 # For Arduino Control
ramp_rate = 0.2/(1/SAMPLING_TIME) # 0.2 per second

# Setup default msg and send it.
msg_delay = str(0)
msg_direction = "," + str(desired_dir)
msg_reset_position =  "," + str(1) 
arduino.write((msg_delay+msg_direction+msg_reset_position).encode())
arduino.write(b'\n')

start_time = time.time()
# Run until keyboard interupt
try:        
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > SAMPLING_TIME:
            start_time = time.time()

            # Read Needed information from DB
            cursor.execute('SELECT Current FROM RPM')
            current_rpm = cursor.fetchone()[0]
            cursor.execute('SELECT Desired FROM RPM')
            desired_rpm = cursor.fetchone()[0]
            cursor.execute('SELECT Current FROM Direction')
            current_dir = cursor.fetchone()[0]    
            cursor.execute('SELECT Desired FROM Direction')
            desired_dir = cursor.fetchone()[0]
            cursor.execute('SELECT Desired FROM Position')
            desired_pos = cursor.fetchone()[0]
            
            if desired_pos == 0:
                # Reset Position button was pressed.
                msg_reset_position =  "," + str(0)
                arduino.write((msg_delay+msg_direction+msg_reset_position).encode())
                arduino.write(b'\n')
                msg_reset_position =  "," + str(1)
                cursor.execute("UPDATE Position SET Desired = ? WHERE ID = ?", (1,1))
                sqlite_connection.commit() 
            
            if current_dir == desired_dir:
                # We don't want directional change so ramp to Desired RPM
                tmp_desired_rpm = desired_rpm 
            else:
                # We want directional change
                if current_rpm == 0:
                    # The speed is zero so we change direction and write it to DB
                    current_dir = desired_dir    
                    cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (desired_dir,1))
                    sqlite_connection.commit()
                else:
                    # We are rotating so we have to ramp down before changing direction 
                    tmp_desired_rpm = 0
            
            if current_rpm != tmp_desired_rpm:
                # We have to change the speed we are rotating at
                if abs(current_rpm - tmp_desired_rpm) < ramp_rate:
                    # handling no overshoot/undershoot
                    tmp_ramp_rate = abs(current_rpm - tmp_desired_rpm)
                else:
                    tmp_ramp_rate = ramp_rate

                if current_rpm < tmp_desired_rpm:
                    # Envoking ramp_rate instead of just jumping to new speed.
                    tmp_desired_rpm = current_rpm + tmp_ramp_rate
                else:
                    tmp_desired_rpm = current_rpm - tmp_ramp_rate
                

                if tmp_desired_rpm < tmp_ramp_rate:
                    # In this case we have a desired speed close to zero or a zero, so we overwrite with 0 speed
                    msg_delay = str(0)
                    msg_direction = "," + str(current_dir)
                    arduino.write((msg_delay+msg_direction+msg_reset_position).encode())
                    arduino.write(b'\n')
                    cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (0,1))
                    sqlite_connection.commit()
                else:
                    # Set new speed to tmp_desired_rpm
                    # Compute delay
                    micro_seconds_per_pulse = int(((60/(tmp_desired_rpm*10.0))/PULSE_PER_ROTATION)*1000000)
                    print(str(micro_seconds_per_pulse) + " RPM: " + str(round(tmp_desired_rpm,1)))
                    msg_delay = str(micro_seconds_per_pulse)
                    msg_direction = "," + str(current_dir)
                    arduino.write((msg_delay+msg_direction+msg_reset_position).encode())
                    arduino.write(b'\n')
                    cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (round(tmp_desired_rpm,1),1))
                    sqlite_connection.commit()

        # Read Position from arduino insert into the shared variable.
        position_in_degrees = arduino.readline().decode().strip()
        with server_thread.Position_lock:
            server_thread.Position = position_in_degrees

except KeyboardInterrupt:
    # Shut down "gracefully"
    to_arduino = str(0) + "," + str(current_dir)
    arduino.write((to_arduino+msg_reset_position).encode())
    arduino.write(b'\n')
    sqlite_connection.close()
    server_thread.stop()
    server_thread.join()


