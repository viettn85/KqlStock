

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


def getStockCodes():
    try:
        URL = "https://finfo-api.vndirect.com.vn/v4/stocks?q=type:IFC,ETF,STOCK~status:LISTED&fields=code,companyName,companyNameEng,shortName,floor,industryName&size=3000"
        data = requests.get(url=URL).json()['data']
        stockCodes = []
        floors = []
        for stock in data:
            if len(stock['code']) == 3:
                stockCodes.append(stock['code'])
                floors.append(stock['floor'])
        df = pd.DataFrame.from_dict({"Code": stockCodes, "Floor": floors})
        df.to_csv("data/stockCodes.csv")
    except Exception as ex:
        logger.exception(ex)
        logger.debug("Load stock codes")


if __name__ == '__main__':
    getStockCodes()
