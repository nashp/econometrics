library(openxlsx)
# import time-series packages and their libary of commands
library(xts)
library(tseries)
library(dplyr)
library(urca)
# install.packages("dyn")
library(dyn)
library(xts)

# import data (in CSV format)
raw_data <- read.xlsx("../data/XMasCoursework.xlsx")

full_data <- raw_data %>% dplyr::rename("YEAR" = "X1") %>%
  mutate(LP = log(PGDP), LQ = log(Q), INF = 100 * (LP - lag(LP)), 
         G = 100 * (LQ - lag(LQ)), YEAR = yearmon(YEAR)) %>% 
  filter(YEAR <= 1985 , YEAR >= 1885)

macro.series <- xts(full_data %>% select(-c(YEAR)), order.by = full_data$YEAR)
macro.subset <- macro.series[, c("U", "G", "INF", "RS", "RL")]

autoplot.zoo(macro.subset)


ur.ardl.model <- dyn$lm(U ~ stats::lag(U, k=-1) + 
                      stats::lag(U, k=-2) + 
                      stats::lag(LQ, k=-1) + 
                      stats::lag(LQ, k=-2), data = macro.series)

summary(ur.ardl.model)
plot(ur.ardl.model)
