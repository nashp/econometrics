import pandas as pd


class Curve(object):
    pass


class CommodityCurve(Curve):

    def __init__(self, num_instruments=0):
        self._n_points = num_instruments
        self._futures = self._n_points*[pd.Series()]
        self._curve = None
        self._monthly = None
        self._daily = None
        self._is_monthly = False

    def add_future(self, data, index):
        try:
            self._futures[index - 1] = data
        except IndexError:
            raise

    def append_future(self, data):
        self._futures.append(data)

    def create_curve(self):
        self._curve = pd.concat([f.series() for f in self._futures], axis=1)

    def add_curve(self, curve):
        self._curve = curve

    def curve(self):
        return self._curve

    def plot_latest(self):
        self._curve.iloc[-1].plot()

    def to_monthly(self):
        if not self._is_monthly:
            self._daily = self._curve
            self._curve = self._curve.resample('M').last()
            self._is_monthly = True
        return self._curve

    def to_daily(self):
        if self._is_monthly:
            self._curve = self._daily
            self._is_monthly = False
        return self._curve

