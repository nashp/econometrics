import pandas as pd


class GenericFuture(object):

    def __init__(self, ticker, number, data=None):
        self._ticker = ticker
        self._series = data
        self._clean_series = None
        self._num_na = None
        self._na_tracker = None
        self._monthly = None

    def fill_data(self, data):
        self._series = data

    def clean_data(self):
        self._na_tracker = self._series[self._series.isna()]
        self._num_na = self._na_tracker.isna().sum()
        self._clean_series = self._series.ffill(inplace=False)

    def series(self):
        return self._clean_series

    def monthly(self):
        return self._monthly

    def to_monthly(self):
        self._monthly = self._clean_series.resample('M').last()
        return self._monthly

    def plot(self):
        self._clean_series.plot()


