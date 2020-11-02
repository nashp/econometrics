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
X = as.matrix(sh_data$LE)

reg <- lm(y ~ X)

# Beta = (X'X)^-1 X' y

X <- cbind(rep(1, nrow(X)), X)
beta_hat <- solve(t(X)%*%X) %*% t(X) %*% y

u = y - X %*% beta_hat

static_model_residuals <- u

hist(u)

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

reg <- lm(sh_data$LD ~ sh_data$LDlag + sh_data$LE + sh_data$LElag + sh_data$trend)
summary(reg)

y <- as.matrix(sh_data$LD)
X <- matrix(cbind(sh_data$LDlag, sh_data$LE, sh_data$LElag, sh_data$trend),
            ncol=4, nrow=nrow(sh_data))
X <- cbind(rep(1, nrow(X)), X)

cleaned_data <- na.omit(cbind(y, X))
y <- as.matrix(cleaned_data[,1])
X <- as.matrix(cleaned_data[,2:ncol(cleaned_data)])
Beta_hat <- solve(t(X) %*% X) %*% t(X) %*% y

# 

u = y - X %*% Beta_hat

T <- nrow(y)
k <- ncol(X)
sigma2_hat <- t(u) %*% u /(T-k)
sigma2_hat <- sigma2_hat[,1] 
var_Beta_hat <- sigma2_hat * solve((t(X) %*% X))
serror = sqrt(diag(var_Beta_hat))

tration <- Beta_hat / serror # Higher more significant


# Restricted Model B1 = -gamma
#Model dt = alpha0 + alpha1 dt-1 + B0 et + B1(et-1 -t) + ut
Xr <- cbind(X[,1:3], X[,4] - X[, 5])

beta_hat_restricted <- solve(t(Xr) %*% Xr) %*% t(Xr) %*% y

 
u_restricted <- Xr %*% beta_hat_restricted - y

#TEsting auto correlation 

durbinWatsonTest(model=as.vector(static_model_residuals))
durbinWatsonTest(model=as.vector(u))
durbinWatsonTest(model=as.vector(u_restricted))

# Hyphothesis test like in tutorial

# Chisq is the Wald Test
linearHypothesis(reg,c("sh_data$trend = 0","sh_data$LDlag + sh_data$LE + sh_data$LElag -1  = 0"),test="Chisq")


