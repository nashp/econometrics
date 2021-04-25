import pandas as pd
import numpy as np
import quandl
import datetime as dt

quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'

co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
              "Corn": "CME_C", "Copper": "CME_HG",
              "Hogs": "CME_LN", "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
              "Soy":"CME_S", "Sugar": "ICE_SB", "HeatOil": "CME_HO", "Gasoline": "CME_RB",
              "Lumber": "CME_LB", "NatGas": "CME_NG", "Gold": "CME_GC",
              "Platinum": "CME_PL", "Palladium": "CME_PA", "Silver": "CME_SI"}

commodities = co_tickers.keys()
all_data = pd.read_excel("../data/RawData.xlsx")
all_data = all_data.set_index("Date")
tickers = [co_tickers[c] + "[1-3]$" for c in commodities]
mask = all_data.columns.str.contains("|".join(tickers))
all_data.iloc[:, mask].to_excel("../data/MultipleTestData.xlsx")