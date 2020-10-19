library(readxl)
library(dplyr)
library(ggplot2)
sh_data <- read_excel("../data/Shiller16.xlsx")

sh_data <- sh_data %>% 
  dplyr::mutate(lNSP = log(NSP), dlNSP = lNSP - dplyr::lag(lNSP, n=1), 
                LD = log(ND), LE = log(NE), PO = ND / NE) %>%
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
X <- cbind(rep(1, nrow(X)), X)

reg <- lm(y ~ X)

# Beta = (X'X)^-1 X' y

beta_hat <- solve(t(X)%*%X) %*% t(X) %*% y

u = y - X %*% beta_hat

hist(u)

T <- nrow(y)
k <- ncol(X)
var_Beta_hat <- t(u) %*% u / (T - k)

# Now Var(B) which is = sigma^2 (X' X) ^ -1
# we estimate sigma^2 by u'u/T-k

sigma2_hat <- t(u) %*% u /(T-k)
sigma2_hat <- sigma2_hat[,1] 
var_Beta_hat <- sigma2_hat * solve((t(X) %*% X))

ggplot(data=sh_data) + 
  geom_line(aes(x=LE, y=LD), colour="red") + 
  geom_line(aes(x=LE, y=X%*%beta_hat), colour="blue")

