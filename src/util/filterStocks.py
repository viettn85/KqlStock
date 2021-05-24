from dotenv import load_dotenv
import pandas as pd
import logging
import logging.config
import os
from datetime import datetime

results = 'data/market/results/'
filtered = 'data/market/intraday/'

def filterByVol():
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(results)))
    vcb = readFile("VCB", results)
    startDate = "2021-01-01"
    vcb = vcb.loc[:startDate]
    count = 0
    # csvFiles = ["AAA.csv"]
    for csv in csvFiles:
        df = readFile(csv[0:3], results)
        if len(df) == 0:
            continue
        subDf = df.loc[:startDate]
        if len(vcb) > (len(subDf[subDf.Volume > 0]) + 3):
            continue
        if min(subDf[subDf.Volume > 0]['Volume']) < 10000:
            continue
        print("Read {} {} rows {}".format(csv, len(subDf), len(vcb)))
        df.to_csv("{}{}".format(filtered, csv))
        count = count + 1
    print("Filtered {} stocks".format(count))

def readFile(stock, location):
    df = pd.read_csv("{}{}.csv".format(location, stock))
    df.sort_values(by="date", ascending=False, inplace=True)
    df.rename(columns={'date': 'Date', 'close': 'Close', 'open': 'Open', 'change':'Change', 'high': 'High', 'low': 'Low', 'volume': 'Volume'}, inplace=True)
    df.set_index("Date", inplace=True)
    df = df.loc[:'2020-01-01']
    return df

if __name__ == '__main__':
    filterByVol()
    