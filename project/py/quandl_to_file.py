import pandas as pd
import quandl

quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'
# Brent: ICE_B1/2
# WTI: CME_CL1/2
# GAS: CME_NG
# Heating oil: CME_HO
# Gasoline: CME_RB
# Wht: CME_W1/2 , ICE_IW1/2
# Corn: CME_C1/2, ICE_IC1/2
# Copper: CME_HG1/2
# LEad: MCX_PB1/2
# Aluminium: CME_AL1/2
# Hog: CME_LN
# Cattle: CME_LC
# Coffee KC

co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
              "Corn": "CME_C", "Copper": "CME_HG", "Lead": "MCX_PB",
              "Aluminium": "CME_ALI", "Gas": "CME_NG", "Hogs": "CME_LN",
              "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
              "Sugar": "ICE_SB", "HeatOil": "CME_HO", "Gasoline": "CME_RB",
              "Lumber": "CME_LB", "NaturalGas": "CME_NG", "Gold": "CME_GC", "Silver": "SI",
              "Platinum": "CME_PL", "AUD": "CME_AD", "ZAR": "CME_RA", "NOK": "CME_NJ",
              "CAD": "CME_CD", "UST5": "CME_FV", "UST2": "CME_TU", "UST10": "CME_TY",
              "FedFunds": "CME_FF"}

contract_months = {"F": "Jan", "G": "Feb", "H":"March",
                   "J":"Apr", "K":"May", "M":"Jun", "N": "Jul", "Q": "Aug",
                   "U":"Sept",  "V":"Oct", "X":"Nov", "Z":"Dec"}

co_meta_data_path = "../data/CHRIS_metadata.csv"
co_contract_data_path = "../data/CHRIS_contractdata.csv"

co_meta_data = pd.read_csv(co_meta_data_path)
co_contract_data = pd.read_csv(co_contract_data_path)

mask = co_meta_data["code"].str.contains('|'.join(co_tickers.values()))
quandl_codes = co_meta_data[mask]["code"]
quandl_codes = "CHRIS/" + quandl_codes

n = len(quandl_codes)
price_data = n * [None]
volume_data = n * [None]
open_interest_data = n * [None]
for i in range(n):
    try:
        data = quandl.get(quandl_codes.iloc[i])
        try:
            volume_data[i] = data["Volume"].rename(quandl_codes.iloc[i].replace("CHRIS/", ""))
            #volume_data.append(volume)
        except Exception as e:
            print(e)
            pass

        try:
            if "Prev. Day Open Interest" in data.columns:
                col = "Prev. Day Open Interest"
            elif "Open Interest" in data.columns:
                col = "Open Interest"
            else:
                col = "Previous Day Open Interest"

            open_interest_data[i] = data[col].rename(quandl_codes.iloc[i].replace("CHRIS/", ""))
            #volume_data.append(volume)
        except Exception as e:
            print(e)
            pass

        if "Settle" in data.columns:
            price_col = "Settle"
        else:
            price_col = "Close"
        price_data[i] = data[price_col].rename(quandl_codes.iloc[i].replace("CHRIS/", ""))
    except Exception as e:
        print("Error in: " + quandl_codes.iloc[i] + "With exception: " + e)
        pass

price_data = pd.concat(price_data, axis=1)
volume_data = pd.concat(volume_data, axis=1)
open_interest_data = pd.concat(open_interest_data, axis=1)

with pd.ExcelWriter('../data/RawData.xlsx') as writer:
    price_data.to_excel(writer, sheet_name="Settle")
    volume_data.to_excel(writer, sheet_name="Volume")
    open_interest_data.to_excel(writer, sheet_name="OpenInterest")

def get_quandl_data(tickers):

    n = len(tickers)
    for i in range(n):
        yield tickers[i]
