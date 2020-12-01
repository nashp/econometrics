#Lecture 11B
library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
library(xts)
library(tseries)
library(urca)
raw_data <- read_excel("../data/data11b.xlsx")

series <- xts(raw_data %>% dplyr::select(-c(year)), order.by = as.Date.yearmon(raw_data$year))

summary(ur.df(na.omit(series$ly), type="none", lags = 1))
summary(ur.df(na.omit(series$debt), type="none", lags = 1))
summary(ur.df(na.omit(series$sm), type="none", lags = 1))
