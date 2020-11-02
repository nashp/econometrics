library(Quandl)
Quandl.api_key('Z2WYzGME3qmxnqQgBcdX')
ln1 <- Quandl('CHRIS/CME_LN1', start_date='2000-01-01', end_date='2020-10-27')
ln2 <- Quandl('CHRIS/CME_LN2', start_date='2000-01-01', end_date='2020-10-27')
ln1$Date <- as.Date(ln1$Date)
ln1.settle <- xts(ln1[, c("Settle")], order.by = ln1$Date)
ln2$Date <- as.Date(ln2$Date)
ln2.settle <- xts(ln2[, c("Settle")], order.by = ln2$Date)

ln.carry <- ln1.settle / ln2.settle  - 1
