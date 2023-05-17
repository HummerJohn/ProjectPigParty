
import sqlite3

sqliteConnection = sqlite3.connect('my_database.db')
cursor = sqliteConnection.cursor()
# cursor.execute('DROP TABLE RPM')
# cursor.execute('CREATE TABLE RPM (ID INT, Desired REAL, Current REAL)')
# cursor.execute("INSERT INTO RPM (ID) VALUES (?)", (1,))
# cursor.execute("UPDATE RPM SET Current = ? WHERE ID = ?", (3.0,1))
# cursor.execute("UPDATE RPM SET Desired = ? WHERE ID = ?", (3.0,1))

# cursor.execute('CREATE TABLE Direction (ID INT, Desired INT, Current INT)')
# cursor.execute("INSERT INTO Direction (ID) VALUES (?)", (1,))
# cursor.execute("UPDATE Direction SET Current = ? WHERE ID = ?", (1,1))
# cursor.execute("UPDATE Direction SET Desired = ? WHERE ID = ?", (1,1))

# cursor.execute('CREATE TABLE Position (ID INT, Desired INT, Current INT)')
cursor.execute("INSERT INTO Position (ID) VALUES (?)", (1,))
cursor.execute("UPDATE Position SET Current = ? WHERE ID = ?", (0,1))
cursor.execute("UPDATE Position SET Desired = ? WHERE ID = ?", (0,1))
# cursor.execute("INSERT INTO RPM (Current) VALUES (?)", (3.0,))

# cursor.execute('SELECT Current FROM RPM')
# current_value = cursor.fetchone()[0]
# print(current_value)


# cursor.execute('DROP TABLE RPM')
sqliteConnection.commit()
sqliteConnection.close()

