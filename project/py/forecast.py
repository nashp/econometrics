import pandas as pd
import statsmodels.api as sm
import statsmodels.stats.api as sms
from statsmodels.compat import lzip
from scipy import stats


class Forecast(object):

    def __init__(self):
        self._predictions = None

    def forecast_fx_co_basis(self, ccy, tickers, horizon, window, fx_returns, basis):
        x = fx_returns.join(basis).dropna()
        predictions = pd.DataFrame(index=x.index, columns=horizon * [None])
        rw = pd.DataFrame(index=x.index, columns=horizon * [None])

        for i in range(window, x.shape[0] - horizon):
            y_sample = x.iloc[i - window:i, x.columns.get_loc(ccy)]
            y_new = x.iloc[i:i + horizon, x.columns.get_loc(ccy)]
            x_sample = x.loc[y_sample.index, tickers]
            x_new = x.loc[y_new.index, tickers]
            x_sample = sm.add_constant(x_sample)
            x_new = sm.add_constant(x_new)
            model = sm.OLS(y_sample, x_sample)
            y_hat = model.fit()
            predict = y_hat.predict(x_new)
            predictions.loc[predict.index[0], :] = predict.values
            rw.loc[y_new.index, :] = horizon * [y_sample.mean()]

        predictions.columns = [str(i) + "M" for i in range(1, horizon + 1)]
        rw.columns = [str(i) + "M" for i in range(1, horizon + 1)]

        self._predictions = predictions.join(rw, how="left").join(fx_returns, how="left")
        return self._predictions

