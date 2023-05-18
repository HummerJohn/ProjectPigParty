import sqlite3
import threading

thread_local = threading.local()

def get_database_connection():
    # Get the connection object for the current thread
    if not hasattr(thread_local, 'connection') or thread_local.connection is None:
        # Connect to the database
        thread_local.connection = sqlite3.connect('my_database.db')
    return thread_local.connection

def get_database_cursor():
    # Get the cursor object for the current thread
    if not hasattr(thread_local, 'cursor') or thread_local.cursor is None:
        # Get the database connection for the current thread
        connection = get_database_connection()
        # Create a new cursor
        thread_local.cursor = connection.cursor()
    return thread_local.cursor

def close_database_resources():
    # Close the connection and cursor objects for the current thread
    if hasattr(thread_local, 'cursor') and thread_local.cursor is not None:
        thread_local.cursor.close()
        thread_local.cursor = None
    if hasattr(thread_local, 'connection') and thread_local.connection is not None:
        thread_local.connection.close()
        thread_local.connection = None