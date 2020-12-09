# ARDL/ECM Tutorial Week 9

library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
library(xts)
library(dyn)
library(lubridate)
raw_data <- read_excel("../data/Shiller16.xlsx")

# Because ND & NE have very notiecable trends we can 
# take logs to make these more linear or take a ratio in PO (payout ratio)
full_data <- raw_data %>% 
  dplyr::mutate(lNSP = log(NSP), 
                LD = log(ND), LE = log(NE), PO = ND / NE, 
                LDlag = dplyr::lag(LD, n = 1), LElag = dplyr::lag(LE, n = 1), 
                lCPI = log(CPI),
                lCPIlag = dplyr::lag(lCPI),
                INF = 100 * (lCPI - lCPIlag),
                trend =  row_number(), 
                DeltaD = LD - LDlag,
                DeltaE = LE - LElag,
                DeltaNSP = lNSP - dplyr::lag(lNSP, n = 1),
                Date = yearmon(YEAR)
  ) %>%
  filter(is.finite(NE), is.finite(ND))

#ARDL : dt = a0 + a1dt1 + b0et + b1et1 + ut;
#ECM : dt = a0 + a1dt1 + b0et + b1et1 + ut:


ardl.model <- lm(LD ~ LDlag + LE + LElag, data=full_data)
summary(ardl.model)

ecm.model <- lm(DeltaD ~ LDlag + LElag + DeltaE, data=full_data)
summary(ecm.model)


# dt = 1et + 2(0 + 1et1 dt) + ut

nonlin_mod = nls(DeltaD~c1*c4*DeltaE + c2 * (c3 + c4 * LElag - LDlag), data = full_data, start=list(c1=0.3, c2=0.3, c3=1, c4=1)) 

# Week 8 VAR

data.xts <- xts(full_data %>% dplyr::select(R, RL, INF), order.by = full_data$Date)

data.xts <- data.xts["1950/1990"]
autoplot(data.xts)

summary(ur.df(na.omit(data.xts$R), type="none"))
summary(ur.df(na.omit(data.xts$R), type="drift"))
summary(ur.df(na.omit(data.xts$R), type="trend"))

summary(ur.df(na.trim(data.xts$RL), type="none", lags=0))
summary(ur.df(na.trim(data.xts$RL), type="drift", lags=0))
summary(ur.df(na.trim(data.xts$RL), type="trend", lags=0))

summary(ur.df(data.xts$RL, type="none", lags=1))
summary(ur.df(na.trim(data.xts$RL - stats::lag(data.xts$RL, k=1)), type="drift", lags=0))
summary(ur.df(na.trim(data.xts$RL), type="trend", lags=1))

