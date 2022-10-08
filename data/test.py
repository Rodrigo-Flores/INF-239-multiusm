import pandas as pd

data = pd.read_csv ('ProductosVF2.csv', sep = ';', encoding = 'utf-8')
df = pd.DataFrame(data)
print(df.iloc[0])