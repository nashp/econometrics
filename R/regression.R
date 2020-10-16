library(readxl)
library(dplyr)
library(ggplot2)
le_data <- read_excel("../data/LifeExpGDP17.xlsx")
  
le_data <- le_data %>% mutate(LoPCGDP = log(PCGDP)) 

reg <- lm(LE ~ LoPCGDP, le_data)
summary(reg)
anova(reg)

# y = XB + u

#Matrix form where Beta_hat = (X'X)^-1 X' y

X <- as.matrix(le_data$LoPCGDP, nrow=nrow(le_data))
y <- as.matrix(le_data$LE, nrow=nrow(le_data))
rep(1, nrow(X))
X <- cbind(rep(1, nrow(X)), X)
T <- nrow(X)
k <- ncol(X)
#Errors 

u <- y - X%*%beta_hat


# Now Var(B) which is = sigma^2 (X' X) ^ -1
# we estimate sigma^2 by u'u/T-k

sigma2_hat <- t(u) %*% u /(T-k)
sigma2_hat <- sigma2_hat[,1] 
var_Beta_hat <- sigma2_hat * solve((t(X) %*% X))

std_error <- sqrt(diag(var_Beta_hat))