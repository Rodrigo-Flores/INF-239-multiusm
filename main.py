import pyodbc

# Connect to the database
try:
    conn = pyodbc.connect('Driver={SQL Server};'
                        'Server=LAPTOP-A43RI4HS\SQLEXPRESS;'
                        'Database=test_tarea1_inf239;'
                        'Trusted_Connection=yes;')
    print("Conexión exitosa")
except Exception as e:
    print("Error al conectar a la base de datos")
    print(e)
                        
# Create a cursor
cursor = conn.cursor()

# Execute a query
cursor.execute('SELECT * FROM test_tarea1_inf239.dbo.ProductosVF2')

# Fetch all the rows
rows = cursor.fetchall()

# Print the rows
for row in rows:
    print(row)

# Close the connection
try:
    conn.close()
    print("Conexión cerrada")
except Exception as e:
    print("Error al cerrar la conexión")
    print(e)