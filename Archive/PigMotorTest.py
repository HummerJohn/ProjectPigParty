# #!/usr/bin/python3
# import RPi.GPIO as GPIO
# import time

# DirP = 3
# PulP = 8

# print('Insert Desired RPM: ')
# RotationsPerMinute = 100 #float(input())

# PulsePerRotation = 1000 * 2
# SecondsPerRotation = 60/RotationsPerMinute 
# SecondsPerPulse = SecondsPerRotation/PulsePerRotation # Delay between each Pulse

# GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)    
# GPIO.setup(PulP,GPIO.OUT)
# GPIO.setup(DirP,GPIO.OUT)

# GPIO.output(DirP,GPIO.LOW)

# while 1:
#     GPIO.output(PulP,GPIO.HIGH)
#     time.sleep(SecondsPerPulse)
#     GPIO.output(PulP,GPIO.LOW)
#     time.sleep(SecondsPerPulse)

from threading import Thread, Event
from time import sleep

event = Event()

def modify_variable(var):
    while True:
        for i in range(len(var)):
            var[i] += 1
        if event.is_set():
            break
        sleep(.5)
    print('Stop printing')


my_var = [1, 2, 3]
t = Thread(target=modify_variable, args=(my_var, ))
t.start()
while True:
    try:
        print(my_var)
        sleep(1)
    except KeyboardInterrupt:
        event.set()
        break
t.join()
print(my_var)