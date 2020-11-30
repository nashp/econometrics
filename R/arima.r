# ARDL/ECM Lecture 6B
library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
library(xts)
library(tseries)
library(urca)
sh_data <- read_excel("../data/Shiller16.xlsx")

# Because ND & NE have very notiecable trends we can 
# take logs to make these more linear or take a ratio in PO (payout ratio)
sh_data <- sh_data %>% 
  dplyr::mutate(lNSP = log(NSP), 
                dlNSP = lNSP - dplyr::lag(lNSP, n = 1), 
                LD = log(ND), 
                LE = log(NE), 
                PO = ND / NE, 
                LDlag = dplyr::lag(LD, n = 1), 
                LElag = dplyr::lag(LE, n = 1),
                lNSPlag = dplyr::lag(lNSP, n = 1),
                trend =  row_number(), 
                DeltaD = LD - LDlag,
                DeltaE = LE - LElag, 
                DeltalNSP = lNSP - dplyr::lag(lNSP),
                lPE = log(NSP/NE)) %>%
  filter(is.finite(NE), is.finite(ND))

st = xts(sh_data$lNSP, order.by = as.Date.yearmon(sh_data$YEAR))
pe <-xts(sh_data$lPE, order.by = as.Date.yearmon(sh_data$YEAR))

adf.test(sh_data$lNSP)
test <- ur.df(sh_data$lNSP)
summary(test)
adf.model <- lm(DeltalNSP ~ trend + lNSPlag, data=sh_data)

# st = a1 + b1 st-1 + c1 t + e ARIMA(1, 0, 0)
ar1__ = arima(st, order=c(1, 0, 0), method="ML")
b1 = coef(ar1__)["ar1"]
se = sqrt(diag(vcov(ar1__)))["ar1"]
tratio <- (b1-0)/se
cv <- qt(0.025, df=length(st))

AIC(ar1__)
BIC(ar1__)
# ARIMA(0,1, 0) delta st = a1 + et
ar_1_ = arima(st, order=c(0, 1, 0))
AIC(ar_1_)
BIC(ar_1_)

# delta st = a1 + b2 delta st-1 et + c1 et-1
ar111 = arima(st, order=c(1, 1, 1))
AIC(ar111)
BIC(ar111)

# ARIMA(1, 1, 0) delta st = a1 + b2 delta st-1 + et
ar11_ = arima(st, order=c(1, 1, 0))
AIC(ar11_)
BIC(ar11_)

# ARIMA (0, 1, 1) delta st = a1 + et +  c1 et-1 
ar_11 = arima(st, order=c(0, 1, 1))
AIC(ar_11)
BIC(ar_11)

AIC(ar1__, ar_1_, ar111, ar11_, ar_11)
BIC(ar1__, ar_1_, ar111, ar11_, ar_11)
