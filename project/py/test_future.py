from unittest import TestCase
import pandas as pd
import matplotlib.pyplot as plt
import quandl

from future import GenericFuture


class TestGenericFuture(TestCase):
    filename = "../data/TestData_Brent.xlsx"
    co_meta_data_path = "../data/CHRIS_metadata.csv"
    co_contract_data_path = "../data/CHRIS_contractdata.csv"

    co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
                  "Corn": "CME_C", "Copper": "CME_HG", "Lead": "MCX_PB",
                  "Aluminium": "CME_ALI", "Gas": "CME_NG", "Hogs": "CME_LN",
                  "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
                  "Sugar": "ICE_SB", "HeatOil": "CME_HO", "Gasoline": "CME_RB",
                  "Lumber": "CME_LB", "NaturalGas": "CME_NG", "Gold": "CME_GC",
                  "Platinum": "CME_PL", "AUD": "CME_AD", "ZAR": "CME_RA", "NOK": "CME_NJ",
                  "CAD": "CME_CD", "UST5": "CME_FV", "UST2": "CME_TU", "UST10": "CME_TY",
                  "FedFunds": "CME_FF"}

    def load_data(self):
        self.data = pd.read_excel(TestGenericFuture.filename, index_col="Date")

    def test_fill_data(self):

        self.load_data()
        try:
            future = GenericFuture(ticker="B", number=1)
            tickers = self.data.columns[1:]
            data = self.data.iloc[:, 0]
            ticker = tickers[1]
            number = 1

            future = GenericFuture(ticker=ticker, number=number)

            future.fill_data(data=data)
            future.plot()
            plt.show()

        except Exception as e:
            self.fail()

    def test_clean_data(self):
        self.load_data()
        try:
            future = GenericFuture(ticker="B", number=1)
            tickers = self.data.columns[1:]
            data = self.data.iloc[:, 0]
            ticker = tickers[1]
            number = 1

            future = GenericFuture(ticker=ticker, number=number, data=data)
            future.clean_data()

            if future.missing_count() == 0:
                self.fail()

            print("Missing Data: " + str(future.missing_count()))
            future.plot()
            plt.show()

        except Exception as e:
            self.fail()

    def test_monthly(self):
        self.fail()

    def test_calculate_return(self):
        self.load_data()
        try:
            future = GenericFuture(ticker="B", number=1)
            tickers = self.data.columns[1:]
            data = self.data.iloc[:, 0]
            ticker = tickers[1]
            number = 1

            future = GenericFuture(ticker=ticker, number=number, data=data)
            future.clean_data()
            future.to_monthly()
            future.calculate_return()
            future.returns().plot()

            plt.show()

        except Exception as e:
            self.fail()

    def test_cumulative_return(self):
        self.load_data()
        try:
            future = GenericFuture(ticker="B", number=1)
            tickers = self.data.columns[1:]
            data = self.data.iloc[:, 0]
            ticker = tickers[1]
            number = 1

            future = GenericFuture(ticker=ticker, number=number, data=data)
            future.clean_data()
            future.to_monthly()
            future.calculate_return()
            future.calculate_cumulative_return()
            future.returns().plot()
            future.cumulative_return().plot()
            plt.show()

        except Exception as e:
            self.fail()

    def test_generate_contract_expiries(self):

        try:
            # Contains Tickers for all contracts, name + description and as of dates
            co_meta_data = pd.read_csv(TestGenericFuture.co_meta_data_path)
            # Contains number of available contracts, delivery months (FGHJKMNQUVXZ) + other meta data
            co_contract_data = pd.read_csv(TestGenericFuture.co_contract_data_path).rename(
                columns={"Quandl Code": "QuandlCode"})
            # Test Commodity, should be in co_tickers dictionary
            commodity = "Brent"
            root_ticker = TestGenericFuture.co_tickers[commodity]
            mask = co_meta_data["code"].str.contains(root_ticker + "1$")
            quandl_codes = "CHRIS/" + co_meta_data[mask]["code"]

            near_ticker = quandl_codes.iloc[0]
            raw_data = quandl.get(near_ticker, start_date="2000-01-01").reset_index()
            raw_data = raw_data.rename(columns={"Prev. Day Open Interest": "Previous Day Open Interest"})

            expiries = GenericFuture.generate_contract_expiries(raw_data[["Date", "Previous Day Open Interest"]].copy(),
                                                                root_ticker=root_ticker,
                                                                co_contract_data=co_contract_data,
                                                                generic_contract_months=GenericFuture.contract_months,
                                                                n_contracts=3)

            expiries.to_excel(commodity + "ContractExpiries.xlsx", index=False)

        except Exception as e:
            self.fail(e)

    def test_calculate_basis(self):
        self.load_data()
        try:
            expiries = pd.read_excel("BrentContractExpiries.xlsx")
            root_ticker = "ICE_B"
            generic_futures = [1, 2]
            tickers = [root_ticker + str(i) for i in generic_futures]
            near_future_data = self.data.loc[:, tickers[0]]
            far_future_data = self.data.loc[:, tickers[1]]
            near_future_ticker = tickers[0]
            far_future_ticker = tickers[1]
            near_future = generic_futures[0]
            far_future = generic_futures[1]

            near_future_expiries = expiries[["Date", str(near_future) + "C_Expiry"]].set_index("Date")
            far_future_expiries = expiries[["Date", str(far_future) + "C_Expiry"]].set_index("Date")

            near_future = GenericFuture(ticker=near_future_ticker, number=near_future, data=near_future_data)
            far_future = GenericFuture(ticker=far_future_ticker, number=far_future, data=far_future_data)

            near_future.clean_data()
            far_future.clean_data()

            if near_future.missing_count() == 0 | far_future.missing_count():
                self.fail()

            near_future.set_expiries(near_future_expiries)
            far_future.set_expiries(far_future_expiries)
            basis = near_future.calculate_basis(far_future)

            basis.to_excel("BasisOutput.xlsx")
            basis.plot()
            plt.show()





        except Exception as e:
            self.fail()
