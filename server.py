import http.server
import socketserver
import sqlite3

def ReadFromDatabase():
    # Connect to the database
    sqliteConnection = sqlite3.connect('my_database.db')
    # Create a cursor object
    cursor = sqliteConnection.cursor()
    # Select the value from the slider_value column
    cursor.execute('SELECT Current FROM RPM')
    # Fetch the value
    Desired_RPM_OLD = cursor.fetchone()[0]
    # Close the cursor and the connection
    cursor.close()
    sqliteConnection.close()
    # Return the value
    return Desired_RPM_OLD

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
        if Desired_RPM > 10.0:
            cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (10.0,1))
        elif Desired_RPM < 0:
            cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (0,1))
        else:
            cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (Desired_RPM,1))
    
    sqliteConnection.commit()        
    cursor.close()
    sqliteConnection.close()

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override the log_message method to do nothing
        pass
    
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
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                Desired_RPM_OLD = ReadFromDatabase()
                with open('Slider.html', 'r') as file:
                    content = file.read()
                    content = content.replace('"{0}"', f'"{Desired_RPM_OLD}"')
                    self.wfile.write(bytes(content, 'utf-8'))
            elif self.path == '/current_rpm':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                Desired_RPM_OLD = ReadFromDatabase()
                self.wfile.write(bytes(str(Desired_RPM_OLD), 'utf-8'))
            else:
                self.send_error(404)
                self.end_headers()
        except Exception as e:
            print("Error occurred while handling request:", e)
            import traceback
            traceback.print_exc()
            self.send_error(500, "Internal server error")
            self.end_headers()

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print("Starting server on port ", server_address[1])
    httpd.serve_forever()
