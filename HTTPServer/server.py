import http.server
import socketserver
import threading
import HTTPServer.database as database
import HTTPServer.request_handler as request_handler

class CustomHTTPServer(http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, server_thread):
        self.server_thread = server_thread
        super().__init__(server_address, RequestHandlerClass)
    
class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = None
        self.Position = None
        self.Position_lock = threading.Lock()

    def run(self):
        database.get_database_connection()
        database.get_database_cursor()
        socketserver.TCPServer.allow_reuse_address = True
        server_address = ('', 8080)
        # self.server = http.server.HTTPServer(server_address, RequestHandler)
        self.server = CustomHTTPServer(server_address, request_handler.RequestHandler, self)
        print("Starting server on port", server_address[1])
        
        self.server.RequestHandlerClass.server_thread = self
        self.server.serve_forever()

    def stop(self):
        if self.server is not None:
            print("Stopping server...")
            self.server.shutdown()
            self.server.server_close()
            print("Server stopped.")
            # Disconnect from the database
            database.close_database_resources()
