import sys
import os
import pandas as pd
import logging
import logging.config
from datetime import datetime
from stock import getSecurityList

from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

pd.options.mode.chained_assignment = None 
# logging.config.fileConfig(fname='logs/daily_log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
today = datetime.today().strftime("%Y-%m-%d")

def getCsvFiles(location):
    try:
        entries = os.listdir(location)
        return list(filter(lambda x: os.path.splitext(x)[1], entries))
    except:
        print("Something wrong with file location: {}".format(location))

def updatePrices(realtime_data):
    csvFiles = getCsvFiles(realtime_data)
    print(csvFiles)
    stocks = ",".join(csvFiles)
    stocks = stocks.replace(".csv", "")
    df = getSecurityList(stocks)
    for i in range(len(df)):
        detail = df.iloc[i]
        logger.info("Updating prices for {} on {}".format(detail.Stock, today))
        currentDf = pd.DataFrame([{
            "Date": today,
            'Close': int(detail.Price)/100,
            'Open': int(detail.Reference)/100,
            'High': int(detail.High)/100,
            'Low': int(detail.Low)/100,
            'Change': float(detail.Change),
            'Volume': detail.Volume
        }])
        currentDf['Date'] = pd.to_datetime(currentDf['Date'])
        currentDf.set_index('Date', inplace=True)
        dailyDf = pd.read_csv(realtime_data + detail.Stock + '.csv', parse_dates=True, index_col="Date")
        try:
            dailyDf.drop(datetime.strptime(today, '%Y-%m-%d'), inplace=True)
        except:
            logger.info("First time update on {}".format(today))
        dailyDf = currentDf.append(dailyDf)
        dailyDf.to_csv(realtime_data + detail.Stock + '.csv')
        logger.info("Finished Updating prices for {} on {}".format(detail.Stock, today))

if __name__ == '__main__':
    updatePrices(os.getenv('data_realtime'))
