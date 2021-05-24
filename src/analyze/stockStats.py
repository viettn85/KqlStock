import pandas as pd
import logging
import logging.config
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

matched = os.getenv('transaction_data')
stats_data = os.getenv('stats_data')

def statsStock(stock, date):
    sideAll = pd.read_csv("{}{}-side-all.csv".format(stats_data, date), index_col="Stock")
    sideLimited = pd.read_csv("{}{}-side-limited.csv".format(stats_data, date), index_col="Stock")
    sideBigBoys = pd.read_csv("{}/{}-bigboys.csv".format(os.getenv('stats_data'), date), index_col="Stock")
    print("All transactions")
    print(sideAll.loc[stock:stock])
    print("Limited transactions")
    print(sideLimited.loc[stock:stock])
    print("BigBoys transactions")
    print(sideBigBoys.loc[stock:stock])

if __name__ == '__main__':
    today = datetime.today().strftime("%Y-%m-%d")
    # today = '2020-11-02'
    statsStock(sys.argv[1], today)
