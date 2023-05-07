#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import datetime
import subprocess

PulP = 8
print('Insert Desired RPM: ')
RotationsPerMinute = float(input())

PulsePerRotation = 1000 * 2
SecondsPerRotation = 60/RotationsPerMinute 
SecondsPerPulse = SecondsPerRotation/PulsePerRotation # Delay between each Pulse

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)    
GPIO.setup(PulP,GPIO.OUT)

while 1:
    GPIO.output(PulP,GPIO.HIGH)
    time.sleep(SecondsPerPulse)
    GPIO.output(PulP,GPIO.LOW)
    time.sleep(SecondsPerPulse)
