import pyodbc


conn = pyodbc.connect(
    'Driver={SQL Server};Server=LAPTOP-A43RI4HS\SQLEXPRESS;Database=test_tarea1_inf239;Trusted_Connection=yes;')

cursor = conn.cursor()
cursor.execute('SELECT * FROM test_tarea1_inf239.dbo.productos')
print(cursor.fetchmany(5))

