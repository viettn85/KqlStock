import os
import sys
from datetime import datetime
import requests
import pandas as pd
import traceback
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def getMillisec(date, time=""):
    lastTime = date + " "
    if time == "":
        time = "17:00:00,00"
    if len(time) == 5: # 22:29
        time = time + ":00,00"
    lastTime = lastTime + time
    dateObj = datetime.strptime(lastTime, '%Y-%m-%d %H:%M:%S,%f')
    return (int)(dateObj.timestamp() * 1000)

def clean(data):
    transactionArr = data[data.find("[") + 1: data.rfind("]")].strip()
    if len(transactionArr) < 2:
        print("There is no transaction")
        return []
    else:
        transactionArr = transactionArr.split(",\n")
        transactionList = []
        for transaction in transactionArr:
            transaction = transaction.replace("\n","").replace("\"","")
            transaction = transaction[1:-1]
            details = transaction.split(",")
            transactionList.append([datetime.fromtimestamp(((int)(details[0]))/1000.0).strftime("%Y-%m-%d"), details[1], details[3], details[4], details[5]])
        df = pd.DataFrame(transactionList)
        return df

def save(df, stock, date):
    logger.info("Saving transactions of {} on {}".format(stock, date))
    df.columns = ['Date', "Price", "Volume", "Time", "Type"]
    df = df[['Date', "Time", "Price", "Volume", "Type"]]
    df = df.astype({'Price': 'float64','Volume': 'int64'})
    # df = df[df.Date == date]
    df = df.sort_values(by=["Date", "Time"], ascending=False)
    df.to_csv("{}{}/{}-{}.csv".format(os.getenv('transaction_data'),  date, date, stock), index=False)

def getTransactionsByStock(stock, date, time=""):
    logger.info("Getting transactions of {} on {} {}".format(stock, date, time))
    millisec = getMillisec(date, time)
    PARAMS = {
                'DetailFile': stock,
                'lastTime': millisec,
                'callback': os.getenv('transactionCallback'),
                '_': "1602053384943"
            }
    # URL = "https://plus24.mbs.com.vn/HO.ashx"
    try:
        data = requests.get(url=os.getenv('transactionUrl'), params=PARAMS).text
        df = clean(data)
        if len(df) > 0:
            save(df, stock, date)
        else:
            print("No trading of {} on {}".format(stock, date))
    except:
        print("Cannot get data of {}".format(stock))

def getHistoryTransactionsByStock(stock, fromDate, toDate):
    dates = pd.date_range(fromDate, toDate).tolist()
    for date in dates:
        getTransactions(stock, date.strftime("%Y-%m-%d"))

def getTransactions(stocks, date, time=""):
    try:
        path = os.path.join(os.getenv("transaction_data"), date)
        print(path) 
        os.mkdir(path) 
    except: 
        print("Folder {} existed".format(date))
        traceback.print_exc()
    stockList = []
    if stocks == "all":
        stockList = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(os.getenv("data_market"))))
        stockList = list(map(lambda stock: stock[0:3], stockList))
    else:
        stockList = stocks.split(",")
    print(len(stockList))
    for stock in stockList:
        # print(stock)
        getTransactionsByStock(stock, date, time)

def getHistoryTransactions(stocks, fromDate, toDate):
    stockList = []
    if stocks == "all":
        stockList = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(os.getenv("data_market"))))
        stockList = map(lambda stock: stock[0:3], stockList)
    else:
        stockList = stocks.split(",")
    for stock in stockList:
        getHistoryTransactionsByStock(stock, fromDate, toDate)

if __name__ == '__main__':
    # transactions all 2020-10-07
    # history all 2020-10-01 2020-10-07
    if sys.argv[1] == "matched":
        getTransactions('all', datetime.today().strftime("%Y-%m-%d"))
    if sys.argv[1] == "newTrades":
        if len(sys.argv) == 5:
            getTransactions(sys.argv[2], sys.argv[3], sys.argv[4])
        if len(sys.argv) == 4:
            getTransactions(sys.argv[2], sys.argv[3])
    if sys.argv[1] == "oldTrades":
        getHistoryTransactions(sys.argv[2], sys.argv[3], sys.argv[4])
