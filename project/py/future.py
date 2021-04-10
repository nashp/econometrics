import numpy as np
import pandas as pd
import quandl
import datetime as dt

class GenericFuture(object):

    contract_months = {"Jan": "F", "Feb": "G", "Mar": "H",
                       "Apr": "J", "May": "K", "Jun": "M", "Jul": "N", "Aug": "Q",
                       "Sep": "U", "Oct": "V", "Nov": "X", "Dec": "Z"}

    def __init__(self, ticker, number, data=None):
        self._ticker = ticker
        self._series = data
        self._original_series = None
        self._num_na = None
        self._na_tracker = None
        self._monthly = None
        self._daily = None
        self._is_monthly = False
        self._returns = None
        self._cumulative_return = None
        self._expiry_dates = None
        self._basis = None
        self._number = number

    def fill_data(self, data):
        self._series = data

    def get_quandl(self, quandl_string, **kwargs):
        data = quandl.get(quandl_string, **kwargs)
        if "Settle" in data.columns:
            price_col = "Settle"
        else:
            price_col = "Close"
        self._series = data[price_col].rename(self._ticker)

    def clean_data(self):
        self._na_tracker = self._series[self._series.isna()]
        self._num_na = self._na_tracker.isna().sum()
        if self._original_series is None:
            self._original_series = self._series

        self._series = self._series.ffill(inplace=False)
        return self._series

    def series(self):
        return self._series

    def monthly(self):
        return self._monthly

    def to_monthly(self):
        if not self._is_monthly:
            self._daily = self._series
            self._series = self._series.resample('M').last()
            self._is_monthly = True
        return self._series

    def to_daily(self):
        if self._is_monthly:
            self._series = self._daily
            self._is_monthly = False
        return self._series

    def calculate_return(self):
        self._returns = self._series.pct_change()

    def returns(self):
        if self._returns is None:
            self.calculate_return()
        return self._returns

    def calculate_cumulative_return(self):
        if self._returns is None:
            self.calculate_return()

        self._cumulative_return = self._returns.add(1).cumprod() - 1
        return self._cumulative_return

    def cumulative_return(self):
        return self._cumulative_return

    def plot(self):
        if self._series is not None:
            self._series.plot()

    def missing_count(self):
        return self._num_na

    def contract_number(self):
        return self._number

    def set_expiries(self, expiries):
        self._expiry_dates = expiries

    def expiry_dates(self):
        return self._expiry_dates

    def calculate_basis(self, far_future):

        to_expiry_ff = far_future.expiry_dates().iloc[:, 0] - far_future.series().reset_index().set_index("Date", drop=False)["Date"]
        to_expiry_nf = self.expiry_dates().iloc[:, 0] - self.series().reset_index().set_index("Date", drop=False)["Date"]

        timedelta = to_expiry_ff.dt.days - to_expiry_nf.dt.days
        annual_factor = 365 / timedelta
        annual_factor = annual_factor.loc[:far_future.series().index.max()].copy()
        self._basis = (self.series() / far_future.series() - 1) * annual_factor
        return self._basis

    @staticmethod
    def generate_contract_expiries(ff_open_interest, root_ticker, co_contract_data, generic_contract_months,
                                   n_contracts=3):

        try:
            ff_open_interest["Month"] = ff_open_interest["Date"].transform(lambda x: x.strftime("%b"))
            ff_open_interest["YearMon"] = ff_open_interest["Date"].transform(lambda x: x.strftime("%y-%m"))
        except KeyError as ke:
            raise ke

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
        dates["ContractMonth"] = dates["Month"].apply(lambda x: GenericFuture.contract_months[x])
        mask = co_contract_data["QuandlCode"] == "CHRIS/" + root_ticker
        months = co_contract_data[mask]["Months"]
        dates["IsDeliveryMonth"] = dates["ContractMonth"].apply(lambda x: months.str.contains(x))
        first_dates = dates.groupby(by=["YearMon", "IsDeliveryMonth"], as_index=False)["Date"].first()
        first_dates = first_dates.rename(columns={"Date": "Expiry"})
        first_dates["Expiry"] = first_dates["Expiry"].to_numpy().astype('datetime64[M]')

        for i in range(n_contracts):
            col_name = str(1 + i) + "C_Expiry"
            first_dates[col_name] = first_dates[first_dates["IsDeliveryMonth"]]["Expiry"].shift(-i) + \
                                    dt.timedelta(days=int(expiry_day))

            first_dates.loc[mask, col_name] = np.NaN
            first_dates["IsWeekend"] = first_dates[col_name].transform(lambda x: x.isoweekday()) > 5
            first_dates.loc[first_dates["IsWeekend"],
                            col_name] = first_dates.loc[first_dates["IsWeekend"],
                                                        col_name].transform(
                lambda x: x - dt.timedelta(days=(x.isoweekday() - 5)))
            first_dates[col_name] = first_dates[col_name].bfill()

        exp_cols = first_dates.columns[first_dates.columns.str.contains("C_Expiry")]
        dates = dates.merge(first_dates.drop(["IsWeekend", "IsDeliveryMonth", "Expiry"], axis=1), how="left", on="YearMon")
        mask = dates["IsDeliveryMonth"] & (dates["Date"] > dates["1C_Expiry"])
        dates.loc[mask, exp_cols] = np.NaN
        dates[exp_cols] = dates[exp_cols].bfill()

        return dates

    def __lt__(self, other):
        return self._number < other.contract_number()

    def __le__(self, other):
        return self._number <= other.contract_number()

    def __gt__(self, other):
        return self._number > other.contract_number()

    def __ge__(self, other):
        return self._number >= other.contract_number()

    def __eq__(self, other):
        return self._number == other.contract_number()



