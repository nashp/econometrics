import pandas as pd
import matplotlib.pyplot as plt
import quandl
import seaborn as sns;sns.set()

from future import GenericFuture

co_tickers = {"Brent": "ICE_B", "WTI": "CME_CL", "Wheat": "CME_W",
                  "Corn": "CME_C", "Copper": "CME_HG",
                  "Hogs": "CME_LN", "Coffee": "ICE_KC", "Cotton": "ICE_CT", "Cocoa": "ICE_CC",
                  "Sugar": "ICE_SB", "HeatOil": "CME_HO", "Gasoline": "CME_RB",
                  "Lumber": "CME_LB", "NatGas": "CME_NG", "Gold": "CME_GC",
                  "Platinum": "CME_PL", "Silver": "CME_SI"}


def load_data(start_date="2000-01-01"):
    filename = "../data/MultipleTestData.xlsx"
    data = pd.read_excel(filename, index_col="Date")
    data = data[start_date:]
    return data


def main(**kwargs):
    data = load_data(start_date="2000-01-01")

    quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'
    ust = quandl.get("USTREASURY/YIELD", start_date="2000-01-01")
    all_basis = list()
    f = open('../tex/FFRegressionTables.tex', 'a')
    for co in co_tickers.keys():
        try:
            commodity = co
            expiries = pd.read_excel("../data/" + commodity + "ContractExpiries.xlsx")
            root_ticker = co_tickers[commodity]
            generic_futures = [1, 2]
            tickers = [root_ticker + str(i) for i in generic_futures]
            near_future_data = data.loc[:, tickers[0]]
            far_future_data = data.loc[:, tickers[1]]
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

            basis = near_future.calculate_basis(far_future)
            all_basis.append(basis)

            fit = near_future.famafrench_test(far_future, ust["3 MO"] / 100, log=False, frequency='M')
            print(commodity)
            print(fit.summary())

            f.write(fit.summary().as_latex())
            f.write(co)
        except KeyError:
            print("Error in " + co)
            pass

    f.close()

    all_basis = pd.concat(all_basis, axis=1)
    all_basis = all_basis.resample('M', convention='end').last()
    all_basis.describe().round(2).drop(index="count").to_latex("../tex/SummaryStatistics.tex")
    ax = sns.boxplot(data=all_basis.drop(columns=["CME_RB1", "CME_PL1"]))
    ax.get_figure().savefig("../tex/CYDistribution.png")

    return


if __name__ == "__main__":
    main()




