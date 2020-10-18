import pandas as pd
import math
import numpy as np
from sklearn.linear_model import LinearRegression

filename = "../data/LifeExpGDP17.xlsx"

le_data = pd.read_excel(filename)
le_data["LoPCGDP"] = le_data["PCGDP"].transform(math.log)

# Non Linear Relationshop
le_data.plot.scatter(x='PCGDP', y='LE')

# Linear relationship
le_data.plot.scatter(x='LoPCGDP', y='LE')
X = np.array(le_data.LoPCGDP).reshape(-1, 1)
y = np.array(le_data.LE)

reg = LinearRegression().fit(X=X, y=y)

X = np.concatenate([np.ones(X.shape), X], axis=1)
X_t = np.transpose(X)
# (X'X)^-1X'y

beta_hat = np.linalg.inv(np.matmul(X_t, X))
beta_hat = np.matmul(beta_hat, X_t)
beta_hat = np.matmul(beta_hat, y)





