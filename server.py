import http.server
import socketserver
import sqlite3


# import threading

# import RPi.GPIO as GPIO
# import time

# PulP = 8
# GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)    
# GPIO.setup(PulP,GPIO.OUT)


# Desired_RPM = 30.0 
# Desired_RPM_OLD = 0.0

def WriteToDatabase(Desired_RPM):
    # Connect to the database
    sqliteConnection = sqlite3.connect('my_database.db')
    # Create a cursor object
    cursor = sqliteConnection.cursor()
    # Insert a value into the slider_value column
    
    cursor.execute('SELECT Current FROM RPM')
    Desired_RPM_OLD = cursor.fetchone()[0]
    # Commit the transaction
    
    if Desired_RPM != Desired_RPM_OLD:
        print("Received Desired RPM: ", Desired_RPM)
        if Desired_RPM > 10.0:
            cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (10.0,1))
        elif Desired_RPM < 0:
            cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (0,1))
        else:
            cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (Desired_RPM,1))
            # cursor.execute("INSERT INTO RPM (Desired) VALUES (?)", (Desired_RPM,))
    
    sqliteConnection.commit()        
    cursor.close()
    sqliteConnection.close()


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # global Desired_RPM
        content_length = int(self.headers['Content-Length'])
        Desired_RPM = (float(self.rfile.read(content_length).decode('utf-8')))

        WriteToDatabase(Desired_RPM)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("Slider value received", "utf-8"))
		
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('Slider.html', 'rb') as file:
                self.wfile.write(file.read())
            return

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print("Starting server on port ", server_address[1])
    httpd.serve_forever()


# server_thread = threading.Thread(target=run_server)
# server_thread.start()

# while 1:
#     if Desired_RPM != Desired_RPM_OLD:
#         print("Received Desired RPM: ", Desired_RPM/10)
#         Desired_RPM_OLD = Desired_RPM
#         PulsePerRotation = 1000 * 2
#         SecondsPerRotation = 60/Desired_RPM_OLD 
#         SecondsPerPulse = SecondsPerRotation/PulsePerRotation # Delay between each Pulse
#         print("Seconds per pulse: ", SecondsPerPulse)
#     GPIO.output(PulP,GPIO.HIGH)
#     time.sleep(SecondsPerPulse)
#     GPIO.output(PulP,GPIO.LOW)
#     time.sleep(SecondsPerPulse)

# division by zero



