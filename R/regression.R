library(readxl)
library(dplyr)
library(ggplot2)
le_data <- read_excel("../data/LifeExpGDP17.xlsx")
  
le_data <- le_data %>% mutate(LoPCGDP = log(PCGDP)) 

reg <- lm(LE ~ LoPCGDP, le_data)
summary(reg)
anova(reg)

# Lecture 1

# y = XB + u

#Matrix form where Beta_hat = (X'X)^-1 X' y

X <- as.matrix(le_data$LoPCGDP, nrow=nrow(le_data))
X <- cbind(rep(1, nrow(X)), X)
y <- as.matrix(le_data$LE, nrow=nrow(le_data))
beta_hat <- solve((t(X) %*% X)) %*% t(X) %*% y

T <- nrow(X)
k <- ncol(X)
#Errors 

u <- y - X%*%beta_hat

# Plot

ggplot() + 
  geom_point(aes(x = X[,2], y = y), 
             colour="red") + 
  geom_point(aes(x = X[,2], 
                 y = X %*% beta_hat), 
             colour="blue")

hist(u)
# Now Var(B) which is = sigma^2 (X' X) ^ -1
# we estimate sigma^2 by u'u/T-k

sigma2_hat <- t(u) %*% u /(T-k)
sigma2_hat <- sigma2_hat[,1] 
var_Beta_hat <- sigma2_hat * solve((t(X) %*% X))
# The off diagonals are the covariances of the Beta hats, so how 
#much they move with each other. 

# We don't estimate the variance of the estimator here
# but if we look at the information matrix (see lecture 4)
# it is the second element of the diagonal

std_error <- sqrt(diag(var_Beta_hat))


#Derman Watson?



