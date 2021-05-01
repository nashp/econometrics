from unittest import TestCase
import pandas as pd
import matplotlib.pyplot as plt
import quandl
import seaborn as sns

from future import GenericFuture


class TestGenericFuture(TestCase):
    filename = "../data/MultipleTestData.xlsx"
    co_meta_data_path = "../data/CHRIS_metadata.csv"
    co_contract_data_path = "../data/CHRIS_contractdata.csv"

    co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
              "Corn": "CME_C", "Copper": "CME_HG",
              "Hogs": "CME_LN", "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
              "Soy":"CME_S", "Sugar": "ICE_SB", #"HeatOil": "CME_HO", "Gasoline": "CME_RB", "Palladium": "CME_PA",
              "Lumber": "CME_LB", "NatGas": "CME_NG", "Gold": "CME_GC",
              "Platinum": "CME_PL", "Silver": "CME_SI"}

    non_co_tickers = {
        "AUD": "CME_AD", "ZAR": "CME_RA", "NOK": "CME_NJ",
        "CAD": "CME_CD", "UST5": "CME_FV", "UST2": "CME_TU", "UST10": "CME_TY",
        "FedFunds": "CME_FF"
    }

    def load_data(self, start_date="2000-01-01"):
        self.data = pd.read_excel(TestGenericFuture.filename, index_col="Date")
        self.data = self.data[start_date:]

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
        quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'
        try:
            # Contains Tickers for all contracts, name + description and as of dates
            co_meta_data = pd.read_csv(TestGenericFuture.co_meta_data_path)
            # Contains number of available contracts, delivery months (FGHJKMNQUVXZ) + other meta data
            co_contract_data = pd.read_csv(TestGenericFuture.co_contract_data_path).rename(
                columns={"Quandl Code": "QuandlCode"})
            # Test Commodity, should be in co_tickers dictionary
            for co in TestGenericFuture.co_tickers.keys():
                print(co)
                commodity = co
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

                expiries.to_excel("../data/" + commodity + "ContractExpiries.xlsx", index=False)

        except Exception as e:
            self.fail(e)

    def test_calculate_basis(self):
        self.load_data(start_date="2000-01-01")
        try:
            all_basis = []
            for co in TestGenericFuture.co_tickers.keys():
                try:
                    commodity = co
                    expiries = pd.read_excel("../data/" + commodity + "ContractExpiries.xlsx")
                    root_ticker = TestGenericFuture.co_tickers[commodity]
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

                    near_future.set_expiries(near_future_expiries)
                    far_future.set_expiries(far_future_expiries)

                    basis = near_future.calculate_basis(far_future, log=True, ffill=True)
                    all_basis.append(basis)
                except KeyError:
                    pass

            all_basis = pd.concat(all_basis, axis=1)
            all_basis.to_excel("../data/AllBasisLog.xlsx")
            all_basis = all_basis.resample('M', convention='end').last()
            summary_description = all_basis.describe().round(2).to_latex()
            f = open('../writeup/tables/SummaryStatistics.tex', 'w')
            f.write(summary_description)
            f.close()
            sns.set(rc={"grid.linewidth": 0.6, "figure.figsize": (11.7, 8.27)})
            sns.set_style(style='whitegrid')
            ax = sns.boxplot(data=all_basis)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            ax.get_figure().savefig("../writeup/img/BasisBoxPlot.png")

            
                #from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
                #plot_acf(nb.values.squeeze(), lags=40)
                # basis.plot()
                #lt.show()
                #plot_pacf(near_future.series().values.squeeze(), lags=40)
                #plt.show()

        except Exception as e:
            self.fail(e)

    def test_famafrench_test(self):
        self.load_data(start_date="2000-01-01")
        try:
            quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'
            ust = quandl.get("USTREASURY/YIELD", start_date="2000-01-01")
            f = open('../writeup/tables/FFRegressionTables.tex', 'a')
            for co in TestGenericFuture.co_tickers.keys(): #["Corn", "Brent", "Lumber", "Copper", "Gold", "Wheat"]:
                try:
                    commodity = co
                    expiries = pd.read_excel("../data/" + commodity +"ContractExpiries.xlsx")
                    root_ticker = TestGenericFuture.co_tickers[commodity]
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

                    near_future.set_expiries(near_future_expiries)
                    far_future.set_expiries(far_future_expiries)

                    fit = near_future.famafrench_test(far_future, ust["3 MO"]/100, log=False, frequency='M')
                    print(commodity)
                    print(fit.summary())

                    f.write(fit.summary().as_latex())
                    f.write('''\newline''')
                except KeyError:
                    print("Error in " + co)
                    pass
            f.close()

        except Exception as e:
            self.fail(e)


