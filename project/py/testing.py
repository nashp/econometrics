from future import GenericFuture
from curve import CommodityCurve

import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_excel("../data/CO_Settle_PX.xlsx")

calendar = {"F":"January",
            "G":"February",
            "H":"March",
            "J":"April",
            "K":"May",
            "M":"June",
            "N":"July",
            "Q":"August",
            "U":"September",
            "V":"October",
            "X":"November",
            "Z":"December"}

contract_data = pd.read_csv("../data/CHRIS_contractdata.csv")

# co_tickers = {"ICE_B": "Brent", "CME_BK": "WTI", "CME_W": "Wheat",
#               "CME_C": "Corn", "CME_HG": "Copper", "MCX_PB": "Lead",
#               "CME_ALI": "Aluminium", "CME_NG": "Gas", "CME_LN": "Hogs",
#               "ICE_KC": "Coffee", "ICE_CT": "Cotton", "ICE_CC": "Cocoa",
#               "ICE_SB": "Sugar", "CME_HO": "HeatOil", "CME_RB": "Gasoline"}

co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
              "Corn": "CME_C", "Copper": "CME_HG", "Lead": "MCX_PB",
              "Aluminium": "CME_ALI", "Gas": "CME_NG", "Hogs": "CME_LN",
              "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
              "Sugar": "ICE_SB", "HeatOil": "CME_HO", "Gasoline": "CME_RB"
              }


filename = "../data/TestData_Brent.xlsx"
data = pd.read_excel(filename, index_col="Date")

tickers = data.columns
futures = [GenericFuture(ticker=t, number=int(t.split("_B")[1]), data=data[t]) for t in tickers]
futures.sort()
brent_curve = CommodityCurve(num_instruments=len(futures))

for f in futures:
    brent_curve.add_future(f, f.contract_number())

brent_curve.create_curve()
brent_curve.to_monthly()
brent_curve.plot_latest()
plt.show()

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
X = brent_curve.curve().dropna().to_numpy()
X = StandardScaler().fit_transform(X)
pca = PCA(n_components=5)
principalComponents = pca.fit_transform(X)
principalDf = pd.DataFrame(data=principalComponents,
                           columns=['PC1', 'PC2', 'PC3', 'PC4', 'PC5'])
pca.fit(X)


