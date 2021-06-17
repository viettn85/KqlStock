import os
import sys 
import requests
import logging
import logging.config
import pandas as pd
from datetime import datetime
import random
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')


logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
today = datetime.today().strftime("%Y-%m-%d")


def getAccountBalance():
    try:
        URL = os.getenv('accountBalance')
        # Params
        pKeyAuthenticate = os.getenv('pKeyAuthenticate')
        pMainAccount = os.getenv('pMainAccount')
        pAccountCode = os.getenv('pAccountCode')
        _ = os.getenv('_')
        PARAMS = {
            'pKeyAuthenticate': pKeyAuthenticate,
            'pMainAccount': pMainAccount,
            'pAccountCode': pAccountCode,
            '_': _
        }
        return int(requests.get(url=URL, params=PARAMS).json()['BuyingPower'])
    except Exception as ex:
        logger.exception(ex)
        logger.debug("Exception when getting account balance")
        logger.debug(ex)
        return 0


def extractPrice(data):
    data = data.replace('^ATC', '')
    data = data.replace('^ATO', '')
    prices = data.split("^")
    return {
        "Stock": prices[1],
        "Ceiling": int(prices[2]),
        "Floor": int(prices[3]),
        "Reference": int(prices[4]),
        "BuyPrice3": int(prices[5]),
        "BuyVolume3": int(prices[6]),
        "BuyPrice2": int(prices[7]),
        "BuyVolume2": int(prices[8]),
        "BuyPrice1": int(prices[9]),
        "BuyVolume1": int(prices[10]),
        "Change": int(prices[11]),
        "Price": int(prices[12]),
        "CurrentVolume": int(prices[13]),
        "SellPrice1": int(prices[14]),
        "SellVolume1": int(prices[15]),
        "SellPrice2": int(prices[16]),
        "SellVolume2": int(prices[17]),
        "SellPrice3": int(prices[18]),
        "SellVolume3": int(prices[19]),
        "Volume": int(prices[20]) * 10,
        "Average": int(prices[21]),
        "High": int(prices[22]),
        "Low": int(prices[23]),
        "FB": int(prices[24]), # Foreign Buy
        "FS": int(prices[25]) # Foreign Sell
    }


def getSecurityList(allStocks):
    noStockPerRequest = 40
    if type(allStocks) == str:
        stockList = allStocks.split(',')
    else:
        stockList = allStocks
    count = int(len(stockList) / noStockPerRequest) + 1
    priceDf = pd.DataFrame([])
    for i in range(count):
        subList = stockList[i * noStockPerRequest: (i+1) * noStockPerRequest]
        if len(subList) == 0:
            continue
        stocks = ','.join(subList)
        df = pd.DataFrame([])
        try:
            logger.info("Requesting to get stock prices")
            logger.info(stocks)
            URL = os.getenv('securityList')
            # Params
            pKeyAuthenticate = os.getenv('pKeyAuthenticate')
            pMainAccount = os.getenv('pMainAccount')
            pTradingCenter = os.getenv('pTradingCenter')
            _ = os.getenv('_')
            PARAMS = {
                'pKeyAuthenticate': pKeyAuthenticate,
                'pMainAccount': pMainAccount,
                'pListShare': stocks,
                'pTradingCenter': pTradingCenter,
                '_': _
            }
            content = str(requests.get(url=URL, params=PARAMS).content)
            if "ERR" in content:
                print("ERROR connecting: " + content)
                sys.exit(0)
            details = content.split("|")[3]
            securities = details.split("#")
            securityDetails = []
            logger.info("Extracting stock prices")
            for security in securities:
                securityDetails.append(extractPrice(security))
            df = pd.DataFrame(securityDetails)
            logger.info("Completed the request to get stock prices")
        except Exception as ex:
            logger.exception(ex)
            logging.debug("Exception when getting stock prices")
            logging.debug(ex)
        df.rename(columns={'BuyPrice3': 'BP3', 'BuyVolume3': 'BV3', \
                                'BuyPrice2': 'BP2', 'BuyVolume2': 'BV2', \
                                'BuyPrice1': 'BP1', 'BuyVolume1': 'BV1', \
                                'SellPrice3': 'SP3', 'SellVolume3': 'SV3', \
                                'SellPrice2': 'SP2', 'SellVolume2': 'SV2', \
                                'SellPrice1': 'SP1', 'SellVolume1': 'SV1'}, \
                                inplace=True)
        priceDf = priceDf.append(df)
    return priceDf

def extractATOCPrice(data):
    prices = data.split("^")
    return {
        "Stock": prices[1],
        "BP1": prices[9],
        "BV1": int(prices[10]),
        "SP1": prices[14],
        "SV1": int(prices[15]),
    }

def getATOC(allStocks):
    noStockPerRequest = 40
    if type(allStocks) == str:
        stockList = allStocks.split(',')
    else:
        stockList = allStocks
    # stockList = ['ACB', 'VPB']
    count = int(len(stockList) / noStockPerRequest) + 1
    priceDf = pd.DataFrame([])
    for i in range(count):
        subList = stockList[i * noStockPerRequest: (i+1) * noStockPerRequest]
        if len(subList) == 0:
            continue
        stocks = ','.join(subList)
        df = pd.DataFrame([])
        try:
            URL = os.getenv('securityList')
            # Params
            pKeyAuthenticate = os.getenv('pKeyAuthenticate')
            pMainAccount = os.getenv('pMainAccount')
            pTradingCenter = os.getenv('pTradingCenter')
            _ = os.getenv('_')
            PARAMS = {
                'pKeyAuthenticate': pKeyAuthenticate,
                'pMainAccount': pMainAccount,
                'pListShare': stocks,
                'pTradingCenter': pTradingCenter,
                '_': _
            }
            content = str(requests.get(url=URL, params=PARAMS).content)
            if "ERR" in content:
                print("ERROR connecting: " + content)
                sys.exit(0)
            details = content.split("|")[3]
            securities = details.split("#")
            securityDetails = []
            for security in securities:
                prices = extractATOCPrice(security)
                securityDetails.append(prices)
            df = pd.DataFrame(securityDetails)
        except Exception as ex:
            logger.exception(ex)
            logging.debug("Exception when getting stock prices")
            logging.debug(ex)
        priceDf = priceDf.append(df)
    return priceDf

def orderBuy(stock, volume, price, account):
    try:
        URL = os.getenv('newOrder')
        # Params
        if account == 'acc1':
            # print("NOT USE THIS ACCOUNT NOW!")
            # sys.exit(1)
            pAccountCode = "2664531"
        else:
            pAccountCode = "2664538"

        PARAMS = {
            'pKeyAuthenticate': os.getenv('pKeyAuthenticate'),
            'pMainAccount': os.getenv('pMainAccount'),
            'pTradingCenter': 'HSX',
            'pSide': 'B02',
            'pAccount': pAccountCode,
            'pShareCode': stock,
            'pVolume': volume,
            'pPrice': price,
            'pPin': os.getenv('PIN'),
            'pDupOrder': 0,
            'pOrderBasket': 0,
            'pNumberOrderBasket': 0,
            'pRandom': random.random(),
            '_': 1589787007344
        }
        content = requests.get(url=os.getenv('newOrder'), params=PARAMS).content
        # if "ERR" in content:
        #     print("ERROR connecting: " + content)
        #     sys.exit(0)
        logger.info(content)
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when buying stock ".format(stock))
        logging.debug(ex)
        return 0


def orderSell(stock, volume, price, account):
    try:
        # Params
        if account == 'acc1':
            # print("NOT USE THIS ACCOUNT NOW!")
            # sys.exit(1)
            pAccountCode = "2664531"
        else:
            pAccountCode = "2664538"
        PARAMS = {
            'pKeyAuthenticate': os.getenv('pKeyAuthenticate'),
            'pMainAccount': os.getenv('pMainAccount'),
            'pTradingCenter': os.getenv('pTradingCenter'),
            'pSide': 'S02',
            'pAccount': pAccountCode,
            'pShareCode': stock,
            'pVolume': volume,
            'pPrice': price,
            'pPin': os.getenv('PIN'),
            'pDupOrder': 0,
            'pOrderBasket': 0,
            'pNumberOrderBasket': 0,
            'pRandom': random.random(),
            '_': 1589787007344
        }
        content = requests.get(url=os.getenv('newOrder'), params=PARAMS).content
        # if "ERR" in content:
        #     print("ERROR connecting: " + content)
        #     sys.exit(0)
        logger.info(content)
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when selling stock ".format(stock))
        logging.debug(ex)
        return 0


def getOrderType(action):
    orderType = ""
    if action.startswith('S'):
        orderType = "Sell"
    if action.startswith('B'):
        orderType = "Buy"
    return orderType


def extractOrder(order):
    details = order.split("^")
    return {
        "OrderID": details[1],
        "Date": today,
        "Time": details[2],
        "Type": getOrderType(details[4]),
        "Stock": details[5],
        "RequestedVol": int(details[6]),
        "MatchedVol": int(details[7]),
        "Price": float(details[8]),
        "Status": details[10],
    }


def getOrders(stock):
    try:
        logger.info("Requesting to get list of orders on {}".format(today))
        URL = os.getenv('getOrders')
        # Params
        pKeyAuthenticate = os.getenv('pKeyAuthenticate')
        pMainAccount = os.getenv('pMainAccount')
        pTradingCenter = os.getenv('pTradingCenter')
        _ = os.getenv('_')
        PARAMS = {
            'pKeyAuthenticate': pKeyAuthenticate,
            'pMainAccount': pMainAccount,
            'pListAccount': '2664538,2664538',
            'pFilterAccount': '',
            'pFilterSide': 'null',
            'pFilterStock': '',
            'pFilterStatus': 'null',
            'pSequence': 0,
            'pPage': 1,
            'pRecordPerPage': 50,
            '_': _
        }
        content = str(requests.get(url=URL, params=PARAMS).content)
        if "ERR" in content:
            print("ERROR connecting: " + content)
            sys.exit(0)
        details = content.split("|")[3]
        if details == " " in content:
            print("There is no order")
            sys.exit(0)
        orders = details.split("#")        
        orderDetails = []
        logger.info("Extracting orders...")
        for order in orders:
            orderDetails.append(extractOrder(order))
        df = pd.DataFrame(orderDetails)
        df = df[['OrderID', 'Date', 'Time', 'Type', 'Stock', 'Price',
                 'MatchedVol', 'RequestedVol', 'Status']]
        logger.info(
            "Complete a request to get list of orders on {}".format(today))
        if stock == 'all':
            return df
        else:
            return df[df.Stock == stock]
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when getting stock prices")
        logging.debug(ex)
        return pd.DataFrame([])

def cancelOrders(order):
    try:
        logger.info("Requesting to cancel order {} on {}".format(order, today))
        PARAMS = {
            'pKeyAuthenticate': os.getenv('pKeyAuthenticate'),
            'pMainAccount': os.getenv('pMainAccount'),
            'pAccount': '2664538',
            'pTradingCenter': '',
            'pOrderNo': order,
            'pPin': os.getenv('PIN'),
            '_': os.getenv('_')
        }
        content = str(requests.get(url=os.getenv('cancelOrders'), params=PARAMS).content)
        if "ERR" in content:
            print("ERROR connecting to cancel order: " + content)
            sys.exit(0)
        print(content)
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when getting stock prices")
        logging.debug(ex)

def scanMarket():
    df = pd.read_csv("data/stockCodes.csv")
    stocks = df.Code
    stocks = ",".join(list(df.Code))
    df = getSecurityList(stocks)
    df.Price = df.Price.div(100)
    df["Value"] = df.Price * df.Volume
    df["Foreign"] = df.FB - df.FS
    df = df[["Stock", "Price", "Volume", "Value", "Foreign", "FB", "FS"]]
    cashFlowDf = df.sort_values(by="Value", ascending=False)[0:50]
    cashFlowDf.to_csv("reports/market/{}_cashflow.csv".format(today), index=False)
    foreign = df.sort_values(by="FB", ascending=False)
    foreign = foreign[0:20]
    foreign = foreign.append(df.sort_values(by="FS", ascending=False)[0:20])
    foreign.to_csv("reports/market/{}_foreign.csv".format(today), index=False)

def updatePotential():
    df = pd.read_csv("data/Potential.csv")
    df = df[["Stock", "BP"]]
    stocks = ",".join(list(df.Stock))
    priceDf = getSecurityList(stocks)
    print(priceDf.columns)
    priceDf.reset_index(drop=True, inplace=True)
    priceDf = priceDf[["Stock", "Low", "Price"]].set_index("Stock")
    df = df.join(priceDf, on='Stock')
    df = df[["Stock", "BP", "Price", "Low"]]
    df.to_csv("data/Potential.csv", index=False)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            scanMarket()
        if sys.argv[1] == "potential":
            updatePotential()
        if sys.argv[1] == "prices":
            if len(sys.argv) == 3:
                print(getSecurityList(sys.argv[2]))
        if sys.argv[1] == "orders":
            if len(sys.argv) == 2:
                print(getOrders('all'))
            else:
                print(getOrders(sys.argv[2]))
        if sys.argv[1] == "cancel":
            cancelOrders(sys.argv[2])
        if sys.argv[1] in ['sell', 's', 'SELL', 'S']:
            orderSell(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        if sys.argv[1] in ['buy', 'b', 'BUY', 'B']:
            orderBuy(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
