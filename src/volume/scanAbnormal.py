import sys
# sys.path.insert(1, 'src/util')
# sys.path.insert(1, 'src/api')
# sys.path.insert(1, 'src/api')
sys.path.append('src/api')
sys.path.append('src/util')

import requests
import pandas as pd
import operator
from datetime import datetime, date, timedelta
from dateutil.relativedelta import *
import sys, os, glob
import traceback

from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

from utils import *
from stock import getSecurityList

pd.set_option('mode.chained_assignment', None)
DATE_FORMAT = "%Y-%m-%d"
today = datetime.now().strftime(DATE_FORMAT)

def getPercentChange(reference, price):
    return round((price - reference)/reference * 100, 2)

def getLastPriceDf(stocks):
    df = pd.DataFrame()
    for stock in stocks:
        stockDf = pd.read_csv('{}{}.csv'.format(os.getenv('data_market'), stock))
        stockDf['Stock'] = stock
        df = df.append(stockDf.head(1))
    df.drop('Date', axis=1, inplace=True)
    df.set_index(['Stock'], inplace=True)
    return df

def getPriceDf():
    stocks = getStocks(os.getenv("high_value_stocks"))
    if isTradingTime():
        priceDf = getSecurityList(stocks)
        priceDf['Change'] = getPercentChange(priceDf.Reference, priceDf.Price)
        priceDf = priceDf[['Stock', 'BP1', 'BV1', 'SP1', 'SV1', 'Change']]
        priceDf.set_index('Stock', inplace=True)
    else:
        priceDf = getLastPriceDf(stocks)
    cashflowDf = pd.read_csv(getLastCashflow(), index_col='Stock')
    priceDf = pd.merge(priceDf, cashflowDf, left_index=True, right_index=True)
    priceDf.Change = priceDf.Change.astype(float)
    return priceDf

def checkPushAction():
    print("PUSH Actions")
    
    # stocks = ['AAA', 'VCB']
    priceDf = getPriceDf()
    priceDf = priceDf[((priceDf.Change < 0) & (priceDf.G > 300) & (priceDf.BB == 0)) | ((priceDf.Change < 0) & (priceDf.BG > 5))]
    print(priceDf)
    return priceDf

def checkPullAction():
    print("PULL Actions")
    stocks = getStocks(os.getenv("high_value_stocks"))
    # stocks = ['AAA', 'VCB']
    priceDf = getPriceDf()
    priceDf = priceDf[((priceDf.Change > 0) & (priceDf.G < -300) & (priceDf.BS == 0)) | ((priceDf.Change > 0) & (priceDf.BG <= -5))]
    print(priceDf)
    return priceDf

def checkAtoAtc():
    priceDf = getPriceDf()

    # priceDf.sort_values('BV1', ascending=False, inplace=True)
    # print("Big Buy Vol:")
    # print(priceDf.head(20))
    # priceDf.sort_values('SV1', ascending=False, inplace=True)
    # print("Big Sell Vol:")
    # print(priceDf.head(20))

def getActionReports():
    message = ""
    priceDf = checkPushAction()
    if len(priceDf) > 0:
        message = message + "\n<H2>PUSH Actions:</H2>"
        message = message + html_style_basic(priceDf)
    priceDf = checkPullAction()
    if len(priceDf) > 0:
        message = message + "\n<H2>PULL Actions:</H2>"
        message = message + html_style_basic(priceDf)
    return message


if __name__ == '__main__':
    checkPullAction()
    checkPushAction()
    # checkAtoAtc()