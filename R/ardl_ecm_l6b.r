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
  dplyr::mutate(lNSP = log(NSP), dlNSP = lNSP - dplyr::lag(lNSP, n = 1), 
                LD = log(ND), LE = log(NE), PO = ND / NE, 
                LDlag = dplyr::lag(LD, n = 1), LElag = dplyr::lag(LE, n = 1), 
                trend =  row_number(), 
                DeltaD = sh_data$LD - sh_data$LDlag
                DeltaE = sh_data$LE - sh_data$LElag, 
                DeltaNSP = sh) %>%
  filter(is.finite(NE), is.finite(ND))

d <- sh_data$LD

X <- matrix(c())

reg = lm(LD ~ LDlag  + LE + LElag + trend, sh_data)
logLik(reg)
u <- resid(reg)
summary(reg)
plot(u)
acf(u)
linearHypothesis(reg,c("trend = 0","LDlag + LE + LElag -1  = 0"),test="Chisq")
linearHypothesis(reg,c("trend = 0","LDlag + LE + LElag -1  = 0"),test="F")
linearHypothesis(reg,c("trend = 0","LElag+LE = 1-LDlag"),test="F")


# F Test
# gamma = 0, a_1 + B_0 + B_1 - 1

R = matrix(c(0, 0, 0, 0, 1, 0, 1, 1, 1, 0), nrow=2, byrow = T)
q = matrix(c(0, 1))
m = nrow(R)
k = ncol(R)
T = nrow(X)
denominator = t((R %*% Beta_hat - q)) %*% solve((R %*% solve(t(X) %*% X) %*% t(R))) %*% (R %*% Beta_hat - q) /2
numerator = t(u) %*% u / (T-k)
Ftest <- denominator / numerator
if(Ftest > qf(0.95, df1=m, df2=T-k)) {
  print("We reject the null hypothesis")
}

reg <- lm(LD ~ LE, sh_data)

#
# $\delta d_t = \alpha_0 + b_0 (\delta e_t) + e_{t-1} b_1 + d_{t-1}a_1 + u_t$

delta_d = sh_data$LD - sh_data$LDlag
delta_e = sh_data$LE - sh_data$LElag

obs <- cbind(delta_d, delta_e, sh_data$LElag, sh_data$LDlag)
colnames(obs) <- c("DeltaD", "DeltaE", "LElag", "LDlag")
obs <- na.trim(data.frame(obs))

reg <- lm(DeltaD ~ DeltaE + LElag + LDlag, obs)
ll_r <- logLik(reg)
u <- resid(reg)
plot(u)
acf(u)

nonlin_mod = nls(DeltaD~c1*c4*DeltaE + c2 * (c3 + c4 * LElag - LDlag), data = obs, start=list(c1=0.3, c2=0.3, c3=1, c4=1)) 
