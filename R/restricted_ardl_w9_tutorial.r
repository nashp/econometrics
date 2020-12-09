# ARDL/ECM Tutorial Week 9

library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
library(xts)
library(dyn)
raw_data <- read_excel("../data/Shiller16.xlsx")

# Because ND & NE have very notiecable trends we can 
# take logs to make these more linear or take a ratio in PO (payout ratio)
full_data <- raw_data %>% 
  dplyr::mutate(lNSP = log(NSP), 
                LD = log(ND), LE = log(NE), PO = ND / NE, 
                LDlag = dplyr::lag(LD, n = 1), LElag = dplyr::lag(LE, n = 1), 
                lCPI = log(CPI),
                lCPIlag = dplyr::lag(lCPI),
                trend =  row_number(), 
                DeltaD = LD - LDlag,
                DeltaE = LE - LElag,
                DeltaNSP = lNSP - dplyr::lag(lNSP, n = 1),
                Date = yearmon(YEAR)
              ) %>%
  filter(is.finite(NE), is.finite(ND))



# Full ARDL dt = a0 + a1dt1 + b0et + b1et1 + 0pt + 1pt1 + ut

full.model <- lm(LD ~ LDlag + LE + LElag + lCPI + lCPIlag, full_data %>% dplyr::filter(Date >= "1950-01-01", Date <= "1990-01-01"))
summary(full.model)

d = xts(full_data$LD, order.by = full_data$Date)
dl = stats::lag(d, k=1)
e = xts(full_data$LE, order.by = full_data$Date)
el = stats::lag(e, k=1)
p = xts(full_data$lCPI, order.by = full_data$Date)
pl = stats::lag(p, k=1)
#
timeframe = "1950/1990"
d.sub = d[timeframe]
d.sub.l <- dl[timeframe]
e.sub = e[timeframe]
e.sub.l = el[timeframe]
p.sub = p[timeframe]
p.sub.l = pl[timeframe]

full.dyn.model <- dyn$lm(d.sub ~ d.sub.l + 
                           e.sub + 
                           e.sub.l + 
                           p.sub + 
                           p.sub.l)
summary(full.dyn.model)
# Restricted Model 1


