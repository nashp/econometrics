library(openxlsx)
# import time-series packages and their libary of commands
library(xts)
library(tseries)
library(dplyr)
library(urca)
# install.packages("dyn")
library(dyn)
library(xts)
library(car)
library(lmtest)
library(urca)

# import data (in CSV format)
raw_data <- read.xlsx("../data/XMasCoursework.xlsx")

full_data <- raw_data %>% dplyr::rename("YEAR" = "X1") %>%
  mutate(LP = log(PGDP), LQ = log(Q), INF = 100 * (LP - lag(LP)), 
         G = 100 * (LQ - lag(LQ)), YEAR = yearmon(YEAR)) %>% 
  filter(YEAR <= 1985 , YEAR >= 1885) %>% mutate(trend = seq(1, n()))

macro.series <- xts(full_data %>% select(-c(YEAR)), order.by = full_data$YEAR)
macro.subset <- macro.series[, c("U", "G", "INF", "RS", "RL")]

autoplot.zoo(macro.subset)

ur.data <- cbind(macro.series$U, 
                 stats::lag(macro.series$U, k=1), 
                 stats::lag(macro.series$U, k=2), 
                 macro.series$LQ,
                 stats::lag(macro.series$LQ, k=1),
                 stats::lag(macro.series$LQ, k=2),
                 macro.series$trend
                 )

ur.ardl.model <- dyn$lm(U ~ stats::lag(U, k=1) + 
                      stats::lag(U, k=2) + 
                        LQ + 
                      stats::lag(LQ, k=1) + 
                      stats::lag(LQ, k=2) + trend, data = ur.data)

summary(ur.ardl.model)
u = resid(ur.ardl.model)

plot(u)
durbinWatsonTest(ur.ardl.model)

#Heteroskedasticity test
u2 <- u * u
summary(dyn$lm(u2 ~ stats::lag(U, k=1) + 
                 stats::lag(U, k=2) + 
                 stats::lag(LQ, k=1) + 
                 stats::lag(LQ, k=2) + trend, data = macro.series))#$fstatistic

yhat <- ur.ardl.model$fitted.values

summary(lm(as.vector(u) ~ (yhat * yhat)))

#Restricted model 

r.data <- cbind(ur.data$U - ur.data$U.1, ur.data$U.1 - ur.data$U.2, ur.data$LQ - ur.data$LQ.1)

r.model <- dyn$lm(U ~ U.1 + LQ, data = r.data)
u <- resid(r.model)

durbinWatsonTest(as.vector(u))


### Arima 

#INF, U, RL, G

summary(ur.df(macro.series$INF)) 
# We say that inflation does not have a 
#unit root as the test statistic lies outside the acceptance region 
#across all significance levels
summary(ur.df(macro.series$U))
# We fail to reject the null hypothesis that unemployment has a unit root and is of at least I(1)
summary(ur.df(macro.series$U, type="trend"))
#Similarly if we include an intercept and trend we fail to reject the null
summary(ur.df(macro.series$RL))
summary(ur.df(macro.series$RL, type="trend"))
summary(ur.df(macro.series$G))
#
adf.test(macro.series$INF)

autoplot(macro.series[, "INF"])

rw.model <- dyn$lm(INF ~ stats::lag(INF, k=1), data=macro.series)
summary(rw.model)
plot(resid(rw.model))

ma.model <- arima(macro.series[, "INF"], order = c(1, 0, 1), method="ML")
rw.model <- arima(macro.series[, "INF"], order = c(1, 0, 0), method="ML")



# INF = INF_t-1 + U_t-1 + RL_t-1 + G_t-1
# RL =  INF_t-1 + U_t-1 + RL_t-1 + G_t-1
# U_t = INF_t-1 + U_t-1 + RL_t-1 + G_t-1
# G_t = INF_t-1 + U_t-1 + RL_t-1 + G_t-1


dyn$lm(INF ~ stats::lag(INF, k=1) + stats::lag(U, k=1) + 
  stats::lag(RL, k=1) + stats::lag(G, k=1), macro.subset)

dyn$lm(RL ~ stats::lag(INF, k=1) + stats::lag(U, k=1) + 
         stats::lag(RL, k=1) + stats::lag(G, k=1), macro.subset)

dyn$lm(U ~ stats::lag(INF, k=1) + stats::lag(U, k=1) + 
         stats::lag(RL, k=1) + stats::lag(G, k=1), macro.subset)

dyn$lm(G ~ stats::lag(INF, k=1) + stats::lag(U, k=1) + 
         stats::lag(RL, k=1) + stats::lag(G, k=1), macro.subset)



var.model <- VAR(na.omit(macro.subset[, c("U", "RL", "INF", "G")]), p=1, type=c("const"))

gc.lag <- 1
grangertest(U ~ RL, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(U ~ INF, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(U ~ G, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)

grangertest(G ~ RL, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(G ~ INF, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(G ~ U, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)

grangertest(INF ~ RL, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(INF ~ G, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(INF ~ U, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)

grangertest(G ~ RL, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(G ~ INF, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)
grangertest(G ~ U, data=macro.subset[, c("U", "RL", "INF", "G")], order = gc.lag)



