import os 
import datetime
import traceback
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')
import pandas as pd
import schedule
import time
import sys
import matplotlib.pyplot as plt
from glob import glob

def reportReducingLevels():
    location = os.getenv("data_realtime")
    # location = os.getenv("data_realtime")
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(location)))
    # csvFiles = ["AAA.csv"]
    stocks = []
    changes = []
    opens = []
    closes = []
    for file in csvFiles:
        try:
            df = pd.read_csv(
                location + file, index_col="Date")
            df = df.loc[:'2020-12-10']
            stocks.append(file[0:3])
            changes.append(pctChange(df.iloc[-1].Open, df.iloc[0].Close))
            opens.append(df.iloc[-1].Open)
            closes.append(df.iloc[0].Close)
        except Exception:
            traceback.print_exc()
            print("Error proceeding {}".format(file))
    df = pd.DataFrame.from_dict({"Stock": stocks, "Change": changes, "Open": opens, "Close": closes})
    df.sort_values(by="Change", ascending=True, inplace=True)
    print(df.head(20))
    df.to_csv("{}reducingRealtime.csv".format(os.getenv("data_report")), index=False)

def shortList(list):
    location = os.getenv("data_high_vol")
    # location = os.getenv("data_realtime")
    stocks = []
    changes = []
    opens = []
    closes = []
    for stock in list:
        try:
            df = pd.read_csv(
                location + stock + ".csv", index_col="Date")
            df = df.loc[:'2020-12-10']
            stocks.append(stock)
            changes.append(pctChange(df.iloc[-1].Open, df.iloc[0].Close))
            opens.append(df.iloc[-1].Open)
            closes.append(df.iloc[0].Close)
        except Exception:
            traceback.print_exc()
            print("Error proceeding {}".format(stock))
    df = pd.DataFrame.from_dict({"Stock": stocks, "Change": changes, "Open": opens, "Close": closes})
    df.sort_values(by="Change", ascending=True, inplace=True)
    print(df.head(20))
    df.to_csv("{}reducingRealtimeBank.csv".format(os.getenv("data_report")), index=False)

def pctChange(open, close):
    return round((close - open)/open * 100, 2)

if __name__ == '__main__':
    reportReducingLevels()
    # shortList(['VCB', 'BID', 'TCB', 'HDB', 'TPB', 'MBB', 'ACB', 'CTG', 'VIB', 'SHB', 'STB', 'EIB'])