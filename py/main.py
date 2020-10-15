import pandas as pd
import math
from sklearn.linear_model import LinearRegression

filename = "../data/LifeExpGDP17.xlsx"

le_data = pd.read_excel(filename)

le_data["LoPCGDP"] = le_data["PCGDP"].transform(math.log)

# Non Linear Relationshop
le_data.plot.scatter(x='PCGDP', y='LE')

# Linear relationship
le_data.plot.scatter(x='LoPCGDP', y='LE')

reg = LinearRegression().fit(X=le_data.LoPCGDP, y=le_data.LE)

