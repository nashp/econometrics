# Week 9 - Class Exercise
library(readxl)
# import time-series packages and their libary of commands

library(tseries)

library(urca)

# install.packages("dyn")
library(dyn)

# import data (in CSV format)
data <- read_excel("../data/Shiller16.xlsx")


# generate log price-earnings ratio LPE
data$LPE <- log(data$NSP/data$NE)

# declare data as time-series data
tsdat <- ts(data, frequency=1, start=c(1871,1))

# generate trime-series plots
plot.ts(tsdat)

# label LPE column of tsdat by lpe
lpe <- tsdat[,10]

# Dickey-Fuller tests
# Note: To be comparable with Stata, need to include obs. for 1949 as well
# The adf.test command uses the tseries package; does not reveal regression output
adf.test(lpe[79:129],alternative=c("stationary"),k=0)
# The ur.df command uses the ucra package and reveals regression output.
# It corresponds to Stata output:
test1 <- ur.df(lpe[79:129],type=c("drift"),lags=0) 
summary(test1)

# Note: To be comparable with Stata, with 1 lagged difference 
# need to include a further obs. for 1948 as well
test2 <- ur.df(lpe[78:129],type=c("drift"),lags=1) 
summary(test2)

test3 <- ur.df(lpe[77:129],type=c("drift"),lags=2) 
summary(test3)

# Note: Need to exclude last to observations for 2015-16 which are missing.
test4 <- ur.df(lpe[1:144],type=c("drift"),lags=0) 
summary(test4)

test5 <- ur.df(lpe[1:144],type=c("drift"),lags=1) 
summary(test5)
# sink()
