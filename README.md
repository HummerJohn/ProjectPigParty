# ProjectPigParty

## Main and MainWindows 
These initiate everything and starts a seperate thread for the server.
Here the communication is also established to the arduino.

## Server
server-py initiates the http server and handles what happens when it is called to stop
it uses request-handler, which takes care of incoming and outgoing trafic to PigParty website.
PigParty.html calls styles and script for looks and functionality respectively

## SQLITE database
my_database is used to handle speed and directional changes.