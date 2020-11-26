library(readxl)
library(dplyr)
library(ggplot2)
library(car)
library(lmtest)

le_data <- read_excel("../data/LifeExpGDP17.xlsx")

le_data <- le_data %>% mutate(LoPCGDP = log(PCGDP)) 

reg <- lm(LE ~ PCGDP, le_data)
summary(reg)
anova(reg)

durbinWatsonTest(model=resid(reg))
acf(resid(reg))

resettest(reg)
