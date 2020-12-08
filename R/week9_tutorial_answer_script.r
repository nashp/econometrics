# Week 9 - Class Exercise
library(readxl)
# import time-series packages and their libary of commands

library(tseries)

library(urca)

# install.packages("dyn")
library(dyn)

# import data (in CSV format)
data <- read_excel("../data/Shiller16.xlsx")

# get logarithmic values
data$LNP <- log(data$ND)
data$LCPI <- log(data$CPI)
data$LNE <- log(data$NE)

# restricted sampe 1950-1990 (accounting for lag)
nd <- ts(data$LNP[79:120])
cpi <- ts(data$LCPI[79:120])
ne <- ts(data$LNE[79:120])

# unrestricted model
fit1 <- dyn$lm(nd ~ lag(nd,-1) + ne + lag(ne,-1) + cpi + lag(cpi,-1))
f1s <- summary(fit1)
f1s
# retrieving SSR
SSR1 <- sum(resid(fit1)^2)

# estimation imposing restrictions on LR coefficients
de <- ts(nd-ne)
dnd <- diff(nd,1,1)
dne <- diff(ne,1,1)
dcpi <- diff(cpi,1,1)
lde <- lag(de,-1)

fit2 <- dyn$lm(dnd ~ dne + dcpi + lag(de,-1))
f2s <- summary(fit2)
f2s
# retrieving SSR
SSR2 <- sum(resid(fit2)^2)

library(car)
# estimation of LR effects
deltaMethod(fit1,"(b3+b4)/(1-b2)",parameterNames=c("b1","b2","b3","b4","b5","b6"))
deltaMethod(fit1,"(b5+b6)/(1-b2)",parameterNames=c("b1","b2","b3","b4","b5","b6"))

# testing linear restrictions on LR coefficients
install.packages("nlWaldTest")
library(nlWaldTest)
nlWaldtest(fit1,"1-b[3]-b[4]=b[2]")
nlWaldtest(fit1,"b[5]=-b[6]")
# fail to reject in both cases
# joint test
nlWaldtest(fit1,"1-b[3]-b[4]=b[2];b[6]=-b[5]")
# fail to reject

# testing nonlinear restrictions of common factor model
nlWaldtest(fit1,"b[4]=-b[2]*b[3];b[6]=-b[2]*b[5]")
# reject

# testing nonlinear restrictions of ECM
nlWaldtest(fit1,"b[4]/b[6]=b[3]/b[5]")
# reject

# F-test of restrictions based on SSR
F <- ((SSR2 - SSR1)/2)/(SSR1/35)
qf(.95,2,35)
# fail to reject

# common factor model
# Note: Output is close to, but does not exactly agree with, Stata output
install.packages("nlme")
library(nlme)
fit3 <- gls(nd ~ ne + cpi, correlation=corARMA(p=1,q=0) )
f3s <- summary(fit3)
f3s

# ECM
# Note: Close, but not exactly like Stata output
install.packages("ecm")
library(ecm)
le <- lag(ne,-1)
lp <- lag(cpi,-1)
xeq <- xtr <- as.data.frame(cbind(le,lp))
fit4 <- ecm(nd,xeq,xtr,includeIntercept=FALSE,lags=1)
summary(fit4)

# sink()