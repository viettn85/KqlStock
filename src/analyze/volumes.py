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

def detectHighTransactions(location, csvFiles, mode):
    
    stocks = []
    counts = []
    buys = []
    sells = []
    T2 = []
    T3 = []
    T5 = []
    T2B = []
    T3B = []
    T5B = []
    T2S = []
    T3S = []
    T5S = []
    
    for file in csvFiles:
        try:
            df = pd.DataFrame()
            if mode == 'daily':
                df = pd.read_csv(location + file)
            if mode == 'combine':
                df = combineTransactions(file[11:14])
            price = df.iloc[0].Price 
            budget = 1000000 # 500M
            vol = budget / price
            df = df[df.Volume > vol]
            stocks.append(file[11:14])
            counts.append(len(df))
            buys.append(len(df[df.Type=='B']))
            sells.append(len(df[df.Type=='S']))
            T2.append(len(df[df.Volume > 2 * vol]))
            T3.append(len(df[df.Volume > 3 * vol]))
            T5.append(len(df[df.Volume > 5 * vol]))
            T2B.append(len(df[(df.Volume > 2 * vol) & (df.Type=='B')]))
            T3B.append(len(df[(df.Volume > 3 * vol) & (df.Type=='B')]))
            T5B.append(len(df[(df.Volume > 5 * vol) & (df.Type=='B')]))
            T2S.append(len(df[(df.Volume > 2 * vol) & (df.Type=='S')]))
            T3S.append(len(df[(df.Volume > 3 * vol) & (df.Type=='S')]))
            T5S.append(len(df[(df.Volume > 5 * vol) & (df.Type=='S')]))
        except Exception:
            print("Error proceeding {}".format(file))
    df = pd.DataFrame.from_dict({"Stock": stocks, "Count": counts, "Buy": buys, "Sell": sells, "2T": T2, "2TB": T2B, "2TS": T2S,
                                     "3T": T3, "3TB": T3B, "3TS": T3S, "5T": T5, "5TB": T5B, "5TS": T5S})
    df.sort_values(by='Count', ascending=False, inplace=True)
    return df

def highTransaction(date):
    location = "{}{}/".format(os.getenv('transaction_data'), date)
    if not os.path.isdir(location):
        print("There is no matched data on {}".format(date))
        sys.exit(1)
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(location)))
    df = detectHighTransactions(location, csvFiles, 'daily')
    df = df.head(10)
    df.to_csv("{}/{}-bigboys.csv".format(os.getenv('stats_data'), date), index=False)

def combineHighTransactions():
    location = "{}{}/".format(os.getenv('transaction_data'), '2020-10-07')
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(location)))
    df = detectHighTransactions(location, csvFiles, 'combine')
    df.to_csv("{}/all.csv".format(os.getenv('data_bigboys')), index=False)

def stockHighTransactions(stock):
    location = "{}{}/".format(os.getenv('transaction_data'), '2020-10-07')
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(location)))
    csvFiles = list(filter(lambda x: (stock in x), csvFiles))
    df = detectHighTransactions(location, csvFiles, 'combine')
    df.to_csv("{}/{}.csv".format(os.getenv('data_bigboys'), stock), index=False)


def combineTransactions(stock):
    subFolders = glob(os.getenv('transaction_data')+"*/")

    subFolders = list(filter(lambda x: ("-" in x), subFolders))
    # filterSub = ['2020-10-26', '2020-10-27', '2020-10-28']
    # subFolders = list(filter(lambda x: (x[-11:-1] in filterSub), subFolders))
    df = pd.DataFrame()
    for folder in subFolders:
        filename = folder[-11:-1] + "-" + stock + ".csv"
        df = df.append(pd.read_csv(folder + filename))
    df.sort_values(by=['Date', 'Time'], ascending=False, inplace=True)
    return df

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if len(sys.argv[1]) == 10:
            highTransaction(sys.argv[1])
        if sys.argv[1] == 'combine':
            combineHighTransactions()
        if len(sys.argv[1]) == 3:
            stockHighTransactions(sys.argv[1])
    if len(sys.argv) == 3:
        dates = pd.date_range(sys.argv[1], sys.argv[2]).tolist()
        for date in dates:
            highTransaction(date.strftime("%Y-%m-%d"))
