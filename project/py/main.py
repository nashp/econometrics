import pandas as pd
import dbnomics
import quandl
# fit an ARIMA model and plot residual errors
from pandas import datetime
from pandas import read_csv
from pandas import DataFrame
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.ar_model import AR
from sklearn.linear_model import LinearRegression

from matplotlib import pyplot

from future import GenericFuture

# Brent: ICE_B1/2
# WTI: CME_BK1/2
# GAS: CME_NG
# Heating oil: CME_HO
# Gasoline: CME_RB
# Wht: CME_W1/2 , ICE_IW1/2
# Corn: CME_C1/2, ICE_IC1/2
# Copper: CME_HG1/2
# LEad: MCX_PB1/2
# Aluminium: CME_AL1/2
# Hog: CME_LN
# Cattle: CME_LC
# Coffee KC




n_contracts = 12

futures = {}

for ticker in co_tickers:

    first_future = "CHRIS/" + ticker + "1"
    second_future = "CHRIS/" + ticker + "2"
    third_future = "CHRIS/" + ticker + "3"
    print(first_future)
    f1 = quandl.get(first_future, start_date='1990-01-01', end_date='2020-12-31')
    #f2 = quandl.get(second_future, start_date='2000-01-01', end_date='2020-12-31')
    #f3 = quandl.get(third_future, start_date='2000-01-01', end_date='2020-12-31')
    if "Settle" in f1.columns:
        price_col = "Settle"
    else:
        price_col = "Close"

    try:
        header = ticker.split(sep="_")[1]
    except IndexError:
        header = ticker.split(sep="_")[0]

    #first_f = pd.concat([first_f, f1[price_col].rename(header)], axis=1)
    #second_f = pd.concat([second_f, f2[price_col].rename(header)], axis=1)
    futures[header] = GenericFuture(ticker=header, number="1", data=f1[price_col].rename(header))




print(futures)


from statsmodels.tsa.stattools import adfuller
from numpy import log
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pmdarima.arima.utils import ndiffs
from statsmodels.tsa.arima.model import ARIMA

gasoline = futures['RB']
gasoline.clean_data()
gasoline_monthly = gasoline.series().resample('M').last()

adfuller(gasoline_monthly.diff().dropna(), regression = "ct")
adfuller(gasoline_monthly.diff().dropna())
plot_acf(gasoline_monthly)
plot_pacf(gasoline_monthly)

gasoline_monthly["2015":"2017"].plot()

ndiffs(gasoline_monthly, test="adf")

plot_pacf(gasoline_monthly.diff().dropna())

model = ARIMA(gasoline_monthly, order=(2,1,2))
model_fit = model.fit()
print(model_fit.summary())

model = pm.auto_arima(gasoline_monthly, seasonal=True, m=12, D=1)