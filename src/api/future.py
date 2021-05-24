import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import pytz
from pytz import timezone
import requests
import schedule
import time

from dotenv import load_dotenv
load_dotenv(dotenv_path='future.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

import warnings
warnings.filterwarnings("ignore")

def getEpoch(date):
    vntz = timezone('Asia/Ho_Chi_Minh')
    dateObj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    loc_dt = vntz.localize(dateObj)
    return (int)(loc_dt.timestamp())

def getMillisec(date, time=""):
    return getEpoch(date, time) * 1000

def getDatetime(epoch):
    # return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
    # return datetime.fromtimestamp(epoch, tz= pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%dT%H:%M:%SZ')
    return datetime.fromtimestamp(epoch, tz= pytz.timezone('GMT')).strftime('%Y-%m-%dT%H:%M:%SZ')

def syncBars(symbol, fromDate, toDate):
    logger.info("Updating bars of {} on {}".format(symbol, toDate))
    params = {
        'symbol': symbol,
        'resolution': 1,
        'from': getEpoch(fromDate),
        'to': getEpoch(toDate)
    }
    print(params)
    headers = {'Content-type': 'application/json; charset=utf-8'}
    return requests.get(url=os.getenv('mbsUrl'), params=params, headers=headers, verify=False).json()
    
def updateBars(data):
    Dates = data['t']
    Opens = data['o']
    Highs = data['h']
    Lows = data['l']
    Closes = data['c']
    Volumes = data['v']
    Dates = map(getDatetime, Dates)
    df = pd.DataFrame(list(zip(Dates, Opens, Closes, Highs, Lows, Volumes)), 
            columns =['Date', 'Open', 'Close', 'High', 'Low', 'Volume']) 
    df.sort_values(by=['Date'], ascending=False, inplace=True)
    df.set_index(["Date"], inplace=True)
    df['Bar_Change'] = df.Close - df.Open
    df['Bar_Pct_Change'] = round(df.Bar_Change / df.Open * 100, 2)
    df['Change'] = df.Close - df.Close.shift(-1)
    df['Pct_Change'] = round(df.Change / df.Close.shift(-1) * 100, 2)
    df['Pattern']=df.apply(lambda x: findPattern(x.Open, x.Close, x.High, x.Low, abs(x.Bar_Pct_Change), abs(x.Pct_Change)),axis=1)
    return df

def findPattern(open, close, high, low, barPctChange, pctChange):
    if close == open:
        if high == open:
            return "Dragonfly"
        if low == open:
            return "Gravestone"
        return "Doji"
    length = high - low
    body = abs(close - open)
    if body <= 0.3 * length:
        top = max(close, open)
        bottom = min(close, open)
        if (barPctChange > 0.01) & (((high - top) > 2 * body) | ((bottom - low) > 2 * body)):
            return "Pin Bar "  + ("Green" if close > open else "Red")
        if (barPctChange > 0) & (((high - top) > 4 * body) | ((bottom - low) > 4 * body)):
            return "Long Pin Bar "  + ("Green" if close > open else "Red")
    if (barPctChange > 0.04) | (pctChange > 0.04):
        return "Long " + ("Green" if close > open else "Red")
    return ""

def proceed(symbol, date, location):
    fromDate = (date + timedelta(days=-1)).strftime("%Y-%m-%d") + " 15:00:00"
    toDate = date.strftime("%Y-%m-%d") + " 15:00:00"
    fromDate = '2020-10-29 15:00:00'
    toDate = '2020-10-30 15:00:00'
    data = syncBars(symbol, fromDate, toDate)
    df = updateBars(data)
    df.to_csv(location + date.strftime("%Y-%m-%d") + ".csv")

if __name__ == '__main__':
    print(os.getenv('mbsUrl'))
    today = datetime.today()
    proceed("VN30", today, os.getenv('data_vn30'))
    proceed("VN30F1M", today, os.getenv('data_f1'))
