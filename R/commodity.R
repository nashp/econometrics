library(Quandl)
library(xts)
library(readxl)
library(rdbnomics)
library(stringr)
library(dplyr)
#Brent: ICE_B1/2
#WTI: CME_BK1/2
#GAS: CME_NG
# Heating oil: CME_HO
# Gasoline: CME_RB
# Wht: CME_W1/2 , ICE_IW1/2
# Corn: CME_C1/2, ICE_IC1/2
# Copper: CME_HG1/2
# LEad: MCX_PB1/2
# Aluminium: CME_AL1/2
# Hog: CME_LN
# Cattle: CME_LC
# Coffee KC


Quandl.api_key('Z2WYzGME3qmxnqQgBcdX')

co_tickers <- c("ICE_B", "CME_BK", "CME_W", "CME_C", 
                "CME_HG", "MCX_PB", "CME_ALI", "CME_NG", 
                "CME_LN", "ICE_KC", "ICE_CT", "ICE_CC", "ICE_SB",
                "CME_HO", "CME_RB")


co_meta_data_path <- "../data/CHRIS_metadata.csv"
omx_meta_data_path <- "../data/NASDAQOMX_metadata.csv"

inflation_data <- rdbnomics::rdb("https://api.db.nomics.world/v22/series/OECD/MEI?limit=1000&offset=0&q=inflation&observations=1&align_periods=1&dimensions=%7B%7D")
inflation_data <- as_tibble(inflation_data)
us_inflation <- inflation_data %>% dplyr::filter(series_code == "USA.CSINFT02.STSA.M") %>%
  dplyr::select(period, original_value, value)
us_inflation <- xts(us_inflation$value, order.by = as.Date(us_inflation$period))
co_meta_data <- read.csv(file = co_meta_data_path)
omx_meta_data <- read.csv(file = omx_meta_data_path)

first_f <- xts()
second_f <- xts()

for(ticker in co_tickers) {

  first_future <- paste("CHRIS/", ticker, "1", sep="")
  second_future <- paste("CHRIS/", ticker, "2", sep="")
  
  f1 <- Quandl(first_future, start_date='2000-01-01', end_date='2020-10-31')
  f2 <- Quandl(second_future, start_date='2000-01-01', end_date='2020-10-31')
  
  if("Settle" %in% colnames(f1)) {
    price_col <- "Settle"
  } else {
    price_col <- "Close"
  }
  
  f1$Date <- as.Date(f1$Date)
  f1.settle <- xts(f1[, c(price_col)], order.by = f1$Date)
  f2$Date <- as.Date(f2$Date)
  f2.settle <- xts(f2[, c(price_col)], order.by = f2$Date)
  
  header <- str_split(ticker, pattern = "_")[[1]][2]
  colnames(f1.settle) <- header
  colnames(f2.settle) <- header
  first_f <- cbind.xts(first_f, f1.settle)
  second_f <- cbind.xts(second_f, f2.settle)

}

