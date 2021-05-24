import os
import sys
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def detectHighVolume():
    dataLocation = getDataLocation()
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(dataLocation)))
    # csvFiles = ["G36.csv"]
    current_time = getCurrentTime()
    stocks = []
    currentVols = []
    previousVols = []
    ratios = []
    closes = []
    lastCloses = []
    changes = []
    for csv in csvFiles:
        stock = csv[-7:-4]
        df = readFile(dataLocation, stock)
        # print(df.iloc[0].Volume)
        if df.iloc[0].Volume < 100000:
            continue
        ratio = round(df.iloc[0].Volume/df.iloc[1].Volume, 2)
        # print(ratio)
        if ((current_time >= "10:15") and (current_time <= "11:30") and (ratio >= 0.8)) or ((current_time >= "11:30") and (current_time <= "14:00") and (ratio >= 1)) or ((current_time >= "14:00") and (current_time <= "15:00") and (ratio >= 1.5)) or (ratio >= 2):
            stocks.append(stock)
            ratios.append(ratio)
            currentVols.append(df.iloc[0].Volume)
            previousVols.append(df.iloc[1].Volume)
            closes.append(df.iloc[0].Close)
            lastCloses.append(df.iloc[1].Close)
            changes.append(round((df.iloc[0].Close - df.iloc[1].Close), 2))

    highVolDf = pd.DataFrame.from_dict({
        "Stock": stocks,
        "Ratio": ratios,
        "Current": currentVols,
        "Previous": previousVols,
        "Last_Close": lastCloses,
        "Close": closes,
        "Change": changes
    })
    highVolDf.sort_values("Ratio", ascending=False, inplace=True)
    print(highVolDf)
    highVolDf.to_csv("data/report/high_volumes.csv", index=False)

def detectPriceZone(stockList):
    dataLocation = getDataLocation()
    following = pd.read_csv("data/{}.csv".format(stockList))
    stocks = []
    prices = []
    signals = []
    opens = []
    highs = []
    lows = []
    closes = []
    for i in range(len(following)):
        stock = following.iloc[i].Stock
        df = pd.read_csv("{}/{}.csv".format(dataLocation, stock))
        if ((stockList == "buy") and (df.iloc[0].Low <= following.iloc[i].Signal)) or ((stockList == "sell") and (df.iloc[0].High >= following.iloc[i].Signal)):
            stocks.append(stock)
            prices.append(following.iloc[i].Price)
            signals.append(following.iloc[i].Signal)
            opens.append(df.iloc[0].Open)
            highs.append(df.iloc[0].High)
            lows.append(df.iloc[0].Low)
            closes.append(df.iloc[0].Close)
    followingDf = pd.DataFrame.from_dict({
        "Stock": stocks,
        "Price": prices,
        "Signal": signals,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes
    })
    if len(followingDf) > 0:
        followingDf.sort_values("Stock", ascending=False, inplace=True)
        print("List of stocks to {}:".format(stockList))
        print(followingDf)
        followingDf.to_csv("data/report/{}.csv".format(stockList), index=False)

def listRiskReward():
    dataLocation = getDataLocation()

def readFile(location, stock):
    return pd.read_csv("{}/{}.csv".format(location, stock))

def getCurrentTime():
    now = datetime.now()
    return now.strftime("%H:%M")

def getDataLocation():
    current_time = getCurrentTime()
    if (current_time >= "10:15") and (current_time <= "21:00"):
        return os.getenv('data_realtime')
    else:
        return os.getenv('data_market_intraday')
    # return os.getenv('data_market_intraday')

if __name__ == '__main__':
    if sys.argv[1] == 'volumes':
        logger.info("Get high volumes")
        detectHighVolume()
    if sys.argv[1] == 'levels':
        logger.info("Update levels")
        detectPriceZone("buy")
        detectPriceZone("sell")
    if sys.argv[1] == 'extract_volumes':
        df = pd.read_csv("data/report/high_volumes.csv")
        stocks = list(df.Stock)
        logger.info("List of stocks having high volumes")
        logger.info(",".join(stocks))
    if sys.argv[1] == 'extract_levels':
        df = pd.read_csv("data/report/buy.csv")
        stocks = list(df.Stock)
        df = pd.read_csv("data/report/sell.csv")
        stocks = stocks + list(df.Stock)
        logger.info("List of stock closed to levels")
        logger.info(",".join(stocks))
