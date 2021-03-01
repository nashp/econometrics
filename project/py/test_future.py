from unittest import TestCase
import pandas as pd
import matplotlib.pyplot as plt

from future import GenericFuture


class TestGenericFuture(TestCase):
    filename = "../data/TestData_Brent.xlsx"

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

