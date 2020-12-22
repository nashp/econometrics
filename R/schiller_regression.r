library(readxl)
library(dplyr)
library(ggplot2)
library(roll)
library(car)
sh_data <- read_excel("../data/Shiller16.xlsx")

# Because ND & NE have very notiecable trends we can 
# take logs to make these more linear or take a ratio in PO (payout ratio)
sh_data <- sh_data %>% 
  dplyr::mutate(lNSP = log(NSP), dlNSP = lNSP - dplyr::lag(lNSP, n = 1), 
                LD = log(ND), LE = log(NE), PO = ND / NE, 
                LDlag = dplyr::lag(LD, n = 1), LElag = dplyr::lag(LE, n = 1), 
                trend =  row_number())%>%
  filter(is.finite(NE), is.finite(ND))

ggplot(data=sh_data) + geom_line(aes(x=YEAR, y=ND), colour="blue") + geom_line(aes(x=YEAR, y=NE), colour="red")

# More volatile series
ggplot(data=sh_data) + geom_line(aes(x=NE, y=ND))

# Log much smoother
ggplot(data=sh_data) + geom_line(aes(x=LE, y=LD))

# The log transformation is probably the better way of
#observing the data

plot(sh_data$PO, type = "l")
hist(sh_data$PO)

# This does not appear to be normally distributed

mu = mean(sh_data$PO, na.rm = T)
serror = sd(sh_data$PO, na.rm = T)
variance = serror * serror

y = as.matrix(sh_data$LD)
X = as.matrix(sh_data$LE) #earnings
reg <- lm(y ~ X)
summary(reg)
# Standard error is 0.2315 because it is log dependent multiply by 100 which gives 
# 23% which is a large error
# Beta0 = -0.42 , Beta1 = 0.8756
# So we are saying that if earnings increase by 1% then dividends increase by 0.87% 
Beta_hat = reg$coefficients[2]
const = reg$coefficients[1]
durbinWatsonTest(reg) # This should be closer to 2
# Beta = (X'X)^-1 X' y

X <- cbind(rep(1, nrow(X)), X)
beta_hat <- solve(t(X)%*%X) %*% t(X) %*% y

u = y - X %*% beta_hat

static_model_residuals <- u

hist(u)
plot(cbind(sh_data$YEAR, static_model_residuals), type="l")
acf(static_model_residuals)# We see autocorrelation

# Now Var(B) which is = sigma^2 (X' X) ^ -1
# we estimate sigma^2 by u'u/T-k
T <- nrow(y)
k <- ncol(X)
sigma2_hat <- t(u) %*% u /(T-k)
sigma2_hat <- sigma2_hat[,1] 
var_Beta_hat <- sigma2_hat * solve((t(X) %*% X))

ggplot(data=sh_data) + 
  geom_line(aes(x=LE, y=LD), colour="red") + 
  geom_line(aes(x=LE, y=X%*%beta_hat), colour="blue")

# multi parameter model

# ld = alpha_0 + alpha_1 * ld_t-1 + beta_0 * le_t + beta_1 * le_t-1 + gamma * t + ut
# y = alpha_0 + alpha_1 y_y-1 + beta_0 * x_t + beta_1 * x_{t-1} + gamma * t + u_{t}
reg <- lm(sh_data$LD ~ sh_data$LDlag + sh_data$LE + sh_data$LElag)# + sh_data$trend)
summary(reg)
durbinWatsonTest(reg) #Better but not yet 2
# We can see that lagged dividends 

y <- as.matrix(sh_data$LD)
X <- matrix(cbind(sh_data$LDlag, sh_data$LE, sh_data$LElag, sh_data$trend),
            ncol=4, nrow=nrow(sh_data))
X <- cbind(rep(1, nrow(X)), X)

plot(cbind(sh_data$YEAR, X %*% reg$coefficients), type="l", col="blue") 
lines(sh_data$YEAR, y, col="red")
cleaned_data <- na.omit(cbind(y, X))
y <- as.matrix(cleaned_data[,1])
X <- as.matrix(cleaned_data[,2:ncol(cleaned_data)])
Beta_hat <- solve(t(X) %*% X) %*% t(X) %*% y

# 

u = y - X %*% Beta_hat

plot(cbind(sh_data$YEAR, u), type="l")

T <- nrow(y)
k <- ncol(X)
sigma2_hat <- t(u) %*% u /(T-k)
sigma2_hat <- sigma2_hat[,1] 
var_Beta_hat <- sigma2_hat * solve((t(X) %*% X))
serror = sqrt(diag(var_Beta_hat))

tratio <- Beta_hat / serror # or null hypothesis is that B = 0, 
# so  if our t-test is outside the acceptance region i.e greater than the 
# 95% then we can reject the null hypothsis


# Restricted Model B1 = -gamma
#Model dt = alpha0 + alpha1 dt-1 + B0 et + B1(et-1 -t) + ut
Xr <- cbind(X[,1:3], X[,4] - X[, 5])

beta_hat_restricted <- solve(t(Xr) %*% Xr) %*% t(Xr) %*% y

 
u_restricted <- Xr %*% beta_hat_restricted - y

(t(u_restricted) %*% u_restricted - t(u) %*% u)/(t(u) %*% u / (T-k))

linearHypothesis(reg,c("sh_data$LE- sh_data$trend = 0"),test="Chisq")
linearHypothesis(reg,c("sh_data$LE- sh_data$trend = 0"),test="Chisq")
#TEsting auto correlation 

durbinWatsonTest(model=as.vector(static_model_residuals))
durbinWatsonTest(model=as.vector(u))
durbinWatsonTest(model=as.vector(u_restricted))

# Hyphothesis test like in tutorial

# Chisq is the Wald Test
linearHypothesis(reg,c("sh_data$trend = 0","sh_data$LDlag + sh_data$LE + sh_data$LElag -1  = 0"),test="Chisq")
linearHypothesis(reg,c("sh_data$trend = 0","sh_data$LDlag + sh_data$LE + sh_data$LElag -1  = 0"),test="F") # F is small sample

# F Test
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




