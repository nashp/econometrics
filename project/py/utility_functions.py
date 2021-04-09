import pandas as pd
import numpy as np
import quandl
import datetime as dt

quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'


def generate_contract_expiries(ff_open_interest, root_ticker, co_contract_data, generic_contract_months, n_contracts=3):
    ff_open_interest = ff_open_interest.reset_index()
    ff_open_interest["Month"] = ff_open_interest["Date"].transform(lambda x: x.strftime("%b"))
    ff_open_interest["YearMon"] = ff_open_interest["Date"].transform(lambda x: x.strftime("%y-%m"))
    ff_open_interest["ContractMonth"] = ff_open_interest["Month"].apply(lambda x: generic_contract_months[x])
    mask = co_contract_data["QuandlCode"] == "CHRIS/" + root_ticker
    months = co_contract_data[mask]["Months"]

    ff_open_interest = ff_open_interest.rename(columns={"Previous Day Open Interest": "OI"})
    ff_open_interest["OI"] = ff_open_interest["OI"].shift(-1)
    ff_open_interest["IsDeliveryMonth"] = ff_open_interest["ContractMonth"].apply(lambda x: months.str.contains(x))
    ff_open_interest = ff_open_interest.merge(ff_open_interest.groupby("YearMon", as_index=False)["OI"].min(),
                                              on="YearMon",
                                              how="left")
    mask = (ff_open_interest["OI_x"] == ff_open_interest["OI_y"]) & (ff_open_interest["IsDeliveryMonth"])
    expiry_day = ff_open_interest.loc[mask, "Date"].dt.day.mode().loc[0]

    dates = pd.DataFrame(pd.bdate_range(start=ff_open_interest["Date"].min(),
                                        end=ff_open_interest["Date"].max() + dt.timedelta(days=720)),
                         columns=["Date"])
    dates["Month"] = dates["Date"].transform(lambda x: x.strftime("%b"))
    dates["YearMon"] = dates["Date"].transform(lambda x: x.strftime("%y-%m"))
    dates["ContractMonth"] = dates["Month"].apply(lambda x: contract_months[x])
    mask = co_contract_data["QuandlCode"] == "CHRIS/" + root_ticker
    months = co_contract_data[mask]["Months"]
    dates["IsDeliveryMonth"] = dates["ContractMonth"].apply(lambda x: months.str.contains(x))
    first_dates = dates.groupby(by=["YearMon", "IsDeliveryMonth"], as_index=False)["Date"].first()
    first_dates = first_dates.rename(columns={"Date": "Expiry"})
    first_dates["Expiry"] = first_dates["Expiry"].to_numpy().astype('datetime64[M]')
    for i in range(n_contracts):
        col_name = str(1+i) + "C_Expiry"
        first_dates[col_name] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-i) + \
                                dt.timedelta(days=int(expiry_day))
        #first_dates["IsWeekend"] = first_dates[col_name].transform(lambda x: x.weekday()) >= 5
        #first_dates.loc[first_dates["IsWeekend"], "Expiry"] = first_dates.loc[first_dates["IsWeekend"], "Expiry"].transform(lambda x: x - (x-5))
        first_dates[col_name] = first_dates[col_name].bfill()

    dates = dates.merge(first_dates, how="left", on="YearMon")

    return dates


co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
              "Corn": "CME_C", "Copper": "CME_HG", "Lead": "MCX_PB",
              "Aluminium": "CME_ALI", "Gas": "CME_NG", "Hogs": "CME_LN",
              "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
              "Sugar": "ICE_SB", "HeatOil": "CME_HO", "Gasoline": "CME_RB",
              "Lumber": "CME_LB", "NaturalGas": "CME_NG", "Gold": "CME_GC",
              "Platinum": "CME_PL", "AUD": "CME_AD", "ZAR": "CME_RA", "NOK": "CME_NJ",
              "CAD": "CME_CD", "UST5": "CME_FV", "UST2": "CME_TU", "UST10": "CME_TY",
              "FedFunds": "CME_FF"}

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

near_ticker = quandl_codes.iloc[0]
raw_data = quandl.get(near_ticker, start_date="2000-01-01")


expiries = generate_contract_expiries(raw_data["Previous Day Open Interest"].copy(),
                                      root_ticker=root_ticker, co_contract_data=co_contract_data,
                                      generic_contract_months=contract_months, n_contracts=3)

expiries.to_excel("CornContractExpiries.xlsx")