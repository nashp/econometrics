# ARDL/ECM Tutorial Week 9

library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
library(xts)
library(dyn)
library(lubridate)
library(urca)

raw_data <- read_excel("../data/electricity.xlsx")
elec.cap <- xts(raw_data$installed_electricty_cap, order.by = zoo::yearmon(raw_data$year))
elec.cap <- cbind(elec.cap, log(elec.cap))
colnames(elec.cap) <- c("Cap", "LogCap")
elec.cap$Trend <- seq(1, nrow(elec.cap))

model <- lm(LogCap ~ lag.xts(LogCap, k=1) + Trend, elec.cap)
summary(model)
plot(residuals(model))

# Mean 0 
y <- elec.cap[, "LogCap"] - mean(elec.cap[, "LogCap"], na.rm = T)
lag1 <- lag.xts(elec.cap[, "LogCap"], k=1) - mean(lag.xts(elec.cap[, "LogCap"], k=1), na.rm = T)
model <- lm(y ~ lag1 + 0)
summary(model)
rho_a <- model$coefficients

model <- lm(LogCap ~ lag.xts(LogCap, k=3), elec.cap)
summary(model)
plot(residuals(model))

lag3 <- lag.xts(elec.cap[, "LogCap"], k=3) - mean(lag.xts(elec.cap[, "LogCap"], k=3), na.rm = T)
model <- lm(y ~ lag3 + 0)
rho_b <- model$coefficients


fc <- forecast(ar.ols(elec.cap[, c("LogCap")], order.max = 1, intercept = T), h=3)
autoplot(fc)



fc <- forecast(elec.cap[, "LogCap"], h=3)
autoplot(fc)
res <- residuals(fc)
autoplot(res)
