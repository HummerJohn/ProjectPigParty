# List running python 
# ps -ef | grep python

from server import run_server
import sqlite3
import threading
import RPi.GPIO as GPIO
import time
import os

server_thread = threading.Thread(target=run_server)
server_thread.start()

PulP = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)    
GPIO.setup(PulP,GPIO.OUT)

sqliteConnection = sqlite3.connect('my_database.db')
# Create a cursor object
cursor = sqliteConnection.cursor()

init = 1
PulsePerRotation = 1000 * 2
try:
    if init == 1:
        cursor.execute('SELECT Current FROM RPM')
        Current_RPM = cursor.fetchone()[0]
        if Current_RPM == 0:
            Current_RPM = 0.1
        SecondsPerRotation = 60/(Current_RPM*10.0)
        SecondsPerPulse = SecondsPerRotation/PulsePerRotation
        init = 0
        os.system('uhubctl -l 1-1 -p 2 -a 1')
        
    while 1:
        cursor.execute('SELECT Current FROM RPM')
        Current_RPM = cursor.fetchone()[0]
        cursor.execute('SELECT Desired FROM RPM')
        Desired_RPM = cursor.fetchone()[0]

        # handle if Desired_RPM == 0
        if Desired_RPM != 0:
            if Desired_RPM != Current_RPM:
                print("Received Desired RPM: ", Desired_RPM)
                SecondsPerRotation = 60/(Desired_RPM*10.0)
                SecondsPerPulse = SecondsPerRotation/PulsePerRotation # Delay between each Pulse
                print("Seconds per pulse: ", SecondsPerPulse)
                cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (Desired_RPM,1))
                sqliteConnection.commit()
            GPIO.output(PulP,GPIO.HIGH)
            time.sleep(SecondsPerPulse)
            GPIO.output(PulP,GPIO.LOW)
            time.sleep(SecondsPerPulse)
        else:
            if Desired_RPM != Current_RPM:
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


