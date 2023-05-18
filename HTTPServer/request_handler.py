import http.server
import HTTPServer.database as database

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        if 'server_thread' in kwargs:
            self.server_thread = kwargs.pop('server_thread')
        super().__init__(*args, **kwargs)
        
    def log_message(self, format, *args):
        # Override the log_message method to do nothing
        pass
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        Desired_RPM = (float(self.rfile.read(content_length).decode('utf-8')))

        sqliteConnection = database.get_database_connection()
        cursor = database.get_database_cursor()
        
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

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("Slider value received", "utf-8"))
		
    def do_GET(self):
        try:
            sqliteConnection = database.get_database_connection()
            cursor = database.get_database_cursor()
            
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                cursor.execute('SELECT Current FROM RPM')
                Desired_RPM_OLD = cursor.fetchone()[0]
                with open('Slider.html', 'r') as file:
                    content = file.read()
                    content = content.replace('"{0}"', f'"{Desired_RPM_OLD}"')
                    self.wfile.write(bytes(content, 'utf-8'))
            elif self.path == '/current_rpm':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                cursor.execute('SELECT Current FROM RPM')
                Desired_RPM_OLD = cursor.fetchone()[0]
                self.wfile.write(bytes(str(Desired_RPM_OLD), 'utf-8'))
            elif self.path == '/desired_rpm':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                cursor.execute('SELECT Desired FROM RPM')
                Desired_RPM = cursor.fetchone()[0]
                self.wfile.write(bytes(str(Desired_RPM), 'utf-8'))                
            elif self.path == '/current_position':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                with self.server_thread.Position_lock:
                    position = self.server_thread.Position
                self.wfile.write(bytes(str(position), 'utf-8'))    
            elif self.path == '/change_direction':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                cursor.execute('SELECT Current FROM Direction')
                # Fetch the value
                Current_Dir = cursor.fetchone()[0]
                if Current_Dir == 1:
                    cursor.execute("UPDATE Direction SET Desired = ? WHERE ID = ?", (0,1))
                else:
                    cursor.execute("UPDATE Direction SET Desired = ? WHERE ID = ?", (1,1))
                # Close the cursor and the connection
                sqliteConnection.commit() 
                self.wfile.write(bytes("Direction changed", 'utf-8'))
            elif self.path == '/change_position':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                cursor.execute("UPDATE Position SET Desired = ? WHERE ID = ?", (0,1))
                sqliteConnection.commit() 
                self.wfile.write(bytes("Zeroed Position", 'utf-8'))
            elif self.path.endswith('.png'):
                # Serve image files
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(self.path[1:], 'rb') as file:
                    self.wfile.write(file.read())            
            else:
                self.send_error(404)
                self.end_headers()
        except Exception as e:
            print("Error occurred while handling request:", e)
            import traceback
            traceback.print_exc()
            self.send_error(500, "Internal server error")
            self.end_headers()