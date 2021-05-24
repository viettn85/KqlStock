import pandas as pd
import logging
import logging.config
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

matched = os.getenv('transaction_data')
stats_data = os.getenv('stats_data')
minBudget = 100000 # 100M

def calculateStats(date, mode):
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(matched + date)))
    # csvFiles = ['2020-11-02-VCB.csv']
    groupByDf = pd.DataFrame()
    for csv in csvFiles:
        stock = csv[-7:-4]
        df = readFile(date, stock, matched)
        if mode != 'all':
            price = df.iloc[0].Price 
            vol = minBudget / price
            df = df[df.Volume > vol]
        # df = df[df.Time <= '11:30:00']
        groupByTypes = df.groupby(['Type']).size().reset_index(name='counts')
        groupByTypes = groupByTypes.pivot_table('counts', [], 'Type')
        groupByTypes.reset_index(drop=True, inplace=True)
        groupByTypes['Stock'] = stock
        if 'B' not in groupByTypes.columns:
            groupByTypes['B'] = 0
        if 'S' not in groupByTypes.columns:
            groupByTypes['S'] = 0
        groupByTypes['Gap'] = groupByTypes.B - groupByTypes.S
        groupByTypes = groupByTypes[['Stock', 'Gap', 'B', 'S']]
        groupByDf = groupByDf.append(groupByTypes)
    groupByDf.sort_values(by=['Gap', 'B'], ascending = False, inplace = True)
    groupByDf.to_csv("{}{}-side-{}.csv".format(stats_data, date, mode), index=False)

def abnormalStocks(date):
    sideAll = pd.read_csv("{}{}-side-all.csv".format(stats_data, date))
    sideAllIncreased = sideAll[sideAll.Gap >= 100]
    sideAllDecreased = sideAll[sideAll.Gap <= -100]
    sideLimited = pd.read_csv("{}{}-side-limited.csv".format(stats_data, date))
    sideLimitedIncreased = sideLimited[sideLimited.Gap >= 50]
    sideLimitedDecreased = sideLimited[sideLimited.Gap <= -50]
    increasedList = union(list(sideAllIncreased.Stock), list(sideLimitedIncreased.Stock))
    decreasedList = union(list(sideAllDecreased.Stock), list(sideLimitedDecreased.Stock))
    print(' - '.join(increasedList))
    print(' - '.join(decreasedList))
    newStats = {
        "DateTime": [date + " " + datetime.today().strftime("%H:%M:%S")],
        "Increased": [' - '.join(increasedList)],
        "Decreased": [' - '.join(decreasedList)],
    }
    df = pd.read_csv("{}abnormal.csv".format(stats_data))
    df = df.append(pd.DataFrame.from_dict(newStats))
    df.sort_values(by='DateTime', ascending=False, inplace=True)
    df.to_csv("{}abnormal.csv".format(stats_data), index=False)

def union(list1, list2): 
    final_list = list(set(list1) | set(list2))
    final_list.sort()
    return final_list

def readFile(date, stock, location):
    return pd.read_csv("{}{}/{}-{}.csv".format(location, date, date, stock))

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
            df.Volume = df.Volume * 10
            df = df[df.Volume * df.Price > budget]
            stocks.append(file[11:14])
            counts.append(len(df))
            buys.append(len(df[df.Type=='B']))
            sells.append(len(df[df.Type=='S']))
            T2.append(len(df[df.Volume * df.Price > 2 * budget]))
            T3.append(len(df[df.Volume * df.Price > 3 * budget]))
            T5.append(len(df[df.Volume * df.Price > 5 * budget]))
            T2B.append(len(df[(df.Volume * df.Price > 2 * budget) & (df.Type=='B')]))
            T3B.append(len(df[(df.Volume * df.Price > 3 * budget) & (df.Type=='B')]))
            T5B.append(len(df[(df.Volume * df.Price > 5 * budget) & (df.Type=='B')]))
            T2S.append(len(df[(df.Volume * df.Price > 2 * budget) & (df.Type=='S')]))
            T3S.append(len(df[(df.Volume * df.Price > 3 * budget) & (df.Type=='S')]))
            T5S.append(len(df[(df.Volume * df.Price > 5 * budget) & (df.Type=='S')]))
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
    # csvFiles = ['2021-01-28-HBC.csv']
    df = detectHighTransactions(location, csvFiles, 'daily')
    # df = df.head(10)
    df.to_csv("{}/{}-bigboys.csv".format(os.getenv('stats_data'), date), index=False)


def splitTransactions(date):
    location = "{}{}/".format(os.getenv('transaction_data'), date)
    if not os.path.isdir(location):
        print("There is no matched data on {}".format(date))
        sys.exit(1)
    csvFiles = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(matched + date)))
    # csvFiles = ['2021-01-28-HBC.csv']
    
    stocks = []
    mornings = []
    afternoons = []
    volumes = []
    for file in csvFiles:
        try:
            df = pd.read_csv(location + file)
            stocks.append(file[11:14])
            subDf = df[df.Time < '12:00:00']
            
            mornings.append(subDf.Volume.sum())
            subDf = df[df.Time > '12:00:00']
            afternoons.append(subDf.Volume.sum())
            volumes.append(df.Volume.sum())
        except Exception:
            print("Error proceeding {}".format(file))

    df = pd.DataFrame.from_dict({"Stock": stocks, "Morning": mornings, "Afternoon": afternoons, "Volume": volumes})
    df['Filtered'] = df.Morning < (df.Afternoon)
    df.sort_values(by="Filtered", ascending=False, inplace=True)
    print(df.Morning.sum(), df.Afternoon.sum())
    df.to_csv("{}/{}-volume.csv".format(os.getenv('stats_data'), date), index=False)

if __name__ == '__main__':
    today = datetime.today().strftime("%Y-%m-%d")
    # today = '2021-01-28'
    calculateStats(today, 'all')
    calculateStats(today, 'limited')
    # abnormalStocks(today)
    highTransaction(today)
    splitTransactions(today)