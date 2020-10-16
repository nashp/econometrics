library(readxl)
library(dplyr)
library(ggplot2)
le_data <- read_excel("../data/LifeExpGDP17.xlsx")
  
le_data <- le_data %>% mutate(LoPCGDP = log(PCGDP)) 

reg <- lm(LE ~ LoPCGDP, le_data)
summary(reg)
anova(reg)