import quandl
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import MonthEnd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
import quandl
import statsmodels.api as sm
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np


fx_data = pd.read_excel("../data/FXData.xlsx")
fx_data["period"] = pd.to_datetime(fx_data["period"])
fx_data = fx_data.set_index("period")["2000-01-01":]
fx_monthly_data = fx_data.resample('M', convention="end").last()
fx_returns = fx_monthly_data.pct_change() * 12
basis = pd.read_excel("AllBasis.xlsx").set_index("Date").drop(columns=["CME_PL1", "CME_NG1.1", "CME_RB1"])
basis_monthly = basis.resample('M', convention="end").last()
quandl.ApiConfig.api_key = 'Z2WYzGME3qmxnqQgBcdX'
raw_ust = quandl.get("USTREASURY/YIELD", start_date="2000-01-01")
ust = raw_ust
ust = ust / 100
ust_st = ust["3 MO"]
ust_st_m = ust_st.resample('M', convention="end").last()
ust_mt = ust["5 YR"]
ust_mt_m = ust_mt.resample('M', convention="end").last()
ust_lt = ust["10 YR"]
ust_lt_m = ust_lt.resample('M', convention="end").last()

window = 24
horizon = 5
ccy = "NOK"
tickers = ["ICE_B1"]
adj_basis = basis_monthly.add(ust_st_m, axis=0)
x = fx_returns.join(adj_basis).dropna()
predictions = pd.DataFrame(index=x.index, columns = horizon * [None])
actual = pd.DataFrame(index=x.index, columns = horizon * [None])
rw = pd.DataFrame(index=x.index, columns = horizon * [None])
predictions.columns = ["1M", "2M", "3M", "4M", "5M"]
for i in range(window, x.shape[0]-horizon):
    y_sample = x.iloc[i-window:i, x.columns.get_loc(ccy)]
    y_new = x.iloc[i:i+horizon, x.columns.get_loc(ccy)]
    x_sample = x.loc[y_sample.index, tickers]
    x_new = x.loc[y_new.index, tickers]
    x_sample = sm.add_constant(x_sample)
    x_new = sm.add_constant(x_new)
    model = sm.OLS(endog=y_sample, exog=x_sample)
    yhat = model.fit()
    print(yhat.summary())
    predict = yhat.predict(x_new)
    predictions.loc[predict.index[0], :] = predict.values
    actual.loc[y_new.index, :] = y_new
    rw.loc[y_new.index, :] = y_sample[-1]

predictions["Actual"] = fx_returns[ccy]
predictions[["Actual", "1M"]].plot()
plt.show()
