#!/bin/bash
uhubctl -l 1-1 -p 2 -a 1
/home/ubuntu/bin/arduino-cli compile --fqbn arduino:avr:uno /home/ubuntu/Repo/ProjectPigParty/GrisseArduinoKode/GrisseArduinoKode.ino
/home/ubuntu/bin/arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno /home/ubuntu/Repo/ProjectPigParty/GrisseArduinoKode/GrisseArduinoKode.ino