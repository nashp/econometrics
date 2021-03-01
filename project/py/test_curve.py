from unittest import TestCase
import pandas as pd
import matplotlib.pyplot as plt

from future import GenericFuture
from curve import CommodityCurve


class TestCommodityCurve(TestCase):
    filename = "../data/TestData_Brent.xlsx"

    def load_data(self):
        self.data = pd.read_excel(TestCommodityCurve.filename, index_col="Date")

    def test_add_future(self):
        try:
            self.load_data()
            tickers = self.data.columns
            futures = [GenericFuture(ticker=t, number=int(t.split("_B")[1]), data=self.data[t]) for t in tickers]
            brent_curve = CommodityCurve(num_instruments=len(futures))

            for f in futures:
                brent_curve.add_future(f, f.contract_number())

        except Exception as e:
            self.fail(e)

    def test_append_future(self):
        try:
            self.load_data()
            tickers = self.data.columns
            futures = [GenericFuture(ticker=t, number=int(t.split("_B")[1]), data=self.data[t]) for t in tickers]
            brent_curve = CommodityCurve()

            for f in futures:
                brent_curve.append_future(f)
            brent_curve.create_curve()

        except Exception as e:
            self.fail(e)

    def test_create_curve(self):
        try:
            self.load_data()
            tickers = self.data.columns
            futures = [GenericFuture(ticker=t, number=int(t.split("_B")[1]), data=self.data[t]) for t in tickers]
            futures.sort()
            brent_curve = CommodityCurve(num_instruments=len(futures))

            for f in futures:
                brent_curve.add_future(f, f.contract_number())

            brent_curve.create_curve()
        except Exception as e:
            raise e

    def test_add_curve(self):
        self.fail()

    def test_curve(self):
        try:
            self.load_data()
            tickers = self.data.columns
            futures = [GenericFuture(ticker=t, number=int(t.split("_B")[1]), data=self.data[t]) for t in tickers]
            futures.sort()
            brent_curve = CommodityCurve(num_instruments=len(futures))

            for f in futures:
                brent_curve.add_future(f, f.contract_number())

            brent_curve.create_curve()

        except Exception as e:
            raise e

    def test_plot_latest(self):
        try:
            self.load_data()
            tickers = self.data.columns
            futures = [GenericFuture(ticker=t, number=int(t.split("_B")[1]), data=self.data[t]) for t in tickers]
            futures.sort()
            brent_curve = CommodityCurve(num_instruments=len(futures))

            for f in futures:
                brent_curve.add_future(f, f.contract_number())

            brent_curve.create_curve()
            brent_curve.plot_latest()
            plt.show()
        except Exception as e:
            raise e

