#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

DirP = 3
PulP = 8

print('Insert Desired RPM: ')
RotationsPerMinute = 100 #float(input())

PulsePerRotation = 1000 * 2
SecondsPerRotation = 60/RotationsPerMinute 
SecondsPerPulse = SecondsPerRotation/PulsePerRotation # Delay between each Pulse

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)    
GPIO.setup(PulP,GPIO.OUT)
GPIO.setup(DirP,GPIO.OUT)

GPIO.output(DirP,GPIO.LOW)

while 1:
    GPIO.output(PulP,GPIO.HIGH)
    time.sleep(SecondsPerPulse)
    GPIO.output(PulP,GPIO.LOW)
    time.sleep(SecondsPerPulse)
