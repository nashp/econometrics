library(readxl)
library(dplyr)
le_data <- read_excel("../data/LifeExpGDP17.xlsx")
  
le_data <- le_data %>% dplyr::