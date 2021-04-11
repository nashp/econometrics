import pandas as pd
import numpy as np
import quandl
import datetime as dt

quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'

def adjust_continuous_future(near_ticker, far_ticker, start_date, end_date):

    first_contract = quandl.get(near_ticker, start_date=start_date, end_date=end_date)
    second_contract = quandl.get(far_ticker, sstart_date=start_date, end_date=end_date)
    first_contract = first_contract.ffill()
    second_contract = second_contract.ffill()

    first_contract = first_contract.rename(columns={"Previous Day Open Interest": "OI"})
    second_contract = second_contract.rename(columns={"Previous Day Open Interest": "OI"})

    first_contract["OI"] = first_contract["OI"].shift(-1)
    second_contract["OI"] = second_contract["OI"].shift(-1)

    contracts = first_contract.join(second_contract, on="Date", how="left", lsuffix="F", rsuffix="S")
    contracts["OIDiff"] = contracts["OIF"] - contracts["OIS"]

    mask = (contracts["OIDiff"].shift(1).transform(np.sign) == 1) & (contracts["OIDiff"].transform(np.sign) == -1)
    contracts.loc[mask, "Roll"] = True
    contracts.loc[mask, "RollDate"] = contracts.loc[mask].index
    contracts["RollDate"] = contracts["RollDate"].bfill()
    contracts["AdjustedPrice"] = contracts["SettleF"]
    mask = contracts["OIDiff"] < 0
    contracts.loc[mask, "AdjustedPrice"] = contracts.loc[mask, "SettleS"]

    return contracts[["AdjustedPrice", "RollDate"]]


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
              "Lumber": "CME_LB", "NaturalGas": "CME_NG", "Gold": "CME_GC",
              "Platinum": "CME_PL", "AUD": "CME_AD", "ZAR": "CME_RA", "NOK": "CME_NJ",
              "CAD": "CME_CD", "UST5": "CME_FV", "UST2": "CME_TU", "UST10": "CME_TY",
              "FedFunds": "CME_FF"}

#contract_months = {"F": "Jan", "G": "Feb", "H":"March",
#                   "J":"Apr", "K":"May", "M":"Jun", "N": "Jul", "Q": "Aug",
#                   "U":"Sept",  "V":"Oct", "X":"Nov", "Z":"Dec"}

contract_months = {"Jan": "F", "Feb": "G", "Mar": "H",
                   "Apr": "J", "May": "K", "Jun": "M", "Jul": "N", "Aug": "Q",
                   "Sep": "U",  "Oct": "V", "Nov": "X", "Dec": "Z"}

co_meta_data_path = "../data/CHRIS_metadata.csv"
co_contract_data_path = "../data/CHRIS_contractdata.csv"

co_meta_data = pd.read_csv(co_meta_data_path)
co_contract_data = pd.read_csv(co_contract_data_path).rename(columns={"Quandl Code": "QuandlCode"})

root_ticker = "CME_C"
mask = co_meta_data["code"].str.contains(root_ticker + "[1-3]$")
quandl_codes = "CHRIS/" + co_meta_data[mask]["code"]

ust = quandl.get("USTREASURY/YIELD", start="1990-01-01")

adj_nf = adjust_continuous_future(near_ticker=quandl_codes.iloc[0], far_ticker=quandl_codes.iloc[1],
                                  start_date="1990-01-01", end_date="2021-03-31")
adj_ff = adjust_continuous_future(near_ticker=quandl_codes.iloc[1], far_ticker=quandl_codes.iloc[2],
                                  start_date="1990-01-01", end_date="2021-03-31")

near_ticker = quandl_codes.iloc[0]
raw_data = quandl.get(near_ticker, start_date="2000-01-01")
df = raw_data.copy()
df["QuandlCode"] = "CHRIS/" + root_ticker
df = pd.merge(df.reset_index(), co_contract_data, on="QuandlCode", how="left")
df["Month"] = df["Date"].transform(lambda x: x.strftime("%b"))
df["YearMon"] = df["Date"].transform(lambda x: x.strftime("%y-%m"))
df["ContractMonth"] = df["Month"].apply(lambda x: contract_months[x])
mask = co_contract_data["QuandlCode"] == "CHRIS/" + root_ticker
months = co_contract_data[mask]["Months"]
df = df.rename(columns={"Previous Day Open Interest": "OI"})
df["OI"] = df["OI"].shift(-1)
df["IsDeliveryMonth"] = df["ContractMonth"].apply(lambda x: months.str.contains(x))
df.groupby(by=["YearMon", "IsDeliveryMonth"])["Date"].first()
df = df.merge(df.groupby("YearMon", as_index=False)["OI"].min(), on="YearMon", how="left")
mask = (df["OI_x"] == df["OI_y"]) & (df["IsDeliveryMonth"])
expiry_day = df.loc[mask, "Date"].dt.day.mode()

first_dates = df.groupby(by=["YearMon", "IsDeliveryMonth"], as_index=False)["Date"].first()
first_dates = first_dates.rename(columns={"Date": "Expiry"})
first_dates["1C"] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-1)
first_dates["2C"] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-2)
first_dates["3C"] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-3)
first_dates["4C"] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-4)
first_dates["5C"] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-5)
first_dates["6C"] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-6)


output = df.merge(first_dates[["YearMon", "Expiry", "1C", "2C", "3C", "4C", "5C", "6C"]], how="left", on="YearMon")
output.loc[~df["IsDeliveryMonth"], "Expiry"] = np.NaN

output.to_excel("CornContract.xlsx")

dates = pd.DataFrame(pd.bdate_range(start=df["Date"].min(), end=df["Date"].max() + dt.timedelta(days=720)),
                  columns=["Date"])
dates["Month"] = dates["Date"].transform(lambda x: x.strftime("%b"))
dates["YearMon"] = dates["Date"].transform(lambda x: x.strftime("%y-%m"))
dates["ContractMonth"] = dates["Month"].apply(lambda x: contract_months[x])
mask = co_contract_data["QuandlCode"] == "CHRIS/" + root_ticker


commodities = ["Corn", "Brent", "Lumber", "Copper"]
all_data = pd.read_excel("output.xlsx")
all_data = all_data.set_index("Date")
tickers = [co_tickers[c] + "[1-3]$" for c in commodities]
mask = all_data.columns.str.contains("|".join(tickers))
all_data.iloc[:, ]