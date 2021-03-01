import pandas as pd
import quandl


class GenericFuture(object):

    def __init__(self, ticker, number, data=None):
        self._ticker = ticker
        self._series = data
        self._original_series = None
        self._num_na = None
        self._na_tracker = None
        self._monthly = None
        self._daily = None
        self._is_monthly = False
        self._number = number

    def fill_data(self, data):
        self._series = data

    def get_quandl(self, quandl_string):
        data = quandl.get(quandl_string)
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

    def plot(self):
        if self._series is not None:
            self._series.plot()

    def missing_count(self):
        return self._num_na

    def contract_number(self):
        return self._number

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

    def __ne__(self, other):
        return not self.__eq__(self, other)

