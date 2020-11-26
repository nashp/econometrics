# ARDL/ECM Lecture 6B

library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
library(xts)
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
                DeltalNSP = lNSP - dplyr::lag(lNSP)) %>%
  filter(is.finite(NE), is.finite(ND))

st = xts(sh_data$lNSP, order.by = as.Date.yearmon(sh_data$YEAR))

adf.test(sh_data$lNSP, k=0)
adf.model <- lm(DeltalNSP ~ trend + lNSPlag, data=sh_data)

ar = arima(st, order=c(1, 0, 0), method="ML")
