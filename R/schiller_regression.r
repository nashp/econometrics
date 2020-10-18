library(readxl)
library(dplyr)
library(ggplot2)
sh_data <- read_excel("../data/Shiller16.xlsx")

sh_data <- sh_data %>% dplyr::mutate(lNSP = log(NSP), dlNSP = lNSP - dplyr::lag(lNSP, n=1)) 
