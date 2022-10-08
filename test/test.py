import pandas as pd
import re

import pyodbc

exp = r'(P|p)ague\s\d+\s(L|l)leve\s\d+'

conn = pyodbc.connect('Driver={SQL Server};Server=LAPTOP-A43RI4HS\SQLEXPRESS;Database=test_tarea1_inf239;Trusted_Connection=yes;')
cursor = conn.cursor()
# select coincidences with the expression
cursor.execute("SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_description LIKE '%Pague%' or prod_description LIKE '%pague%'")
# get the results
rows = cursor.fetchall()
# remove none
rows = [row for row in rows if row is not None]
# row as string
new_rows = []
for row in rows:
    # print(row)
    # check if the description matches the expression
    if re.search(exp, row[2]) is not None:
        # print('match')
        new_rows.append(row)
    else:
        # print('no match')
        pass

for row in new_rows:
    offer = re.search(exp, row[2]).group()
    offer = re.split(r'\s', offer)
    pague = int(offer[1])
    lleve = int(offer[3])

    # insert to oferta table
    print(row[0], '{}x{}'.format(lleve, pague))
    cursor.execute("INSERT INTO test_tarea1_inf239.dbo.Oferta VALUES (?, ?)", row[0], '{}x{}'.format(lleve, pague))

conn.commit()