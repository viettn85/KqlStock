import http.cookiejar as cookielib
from seleniumUtils import *
import sys
import os 
from datetime import datetime
import shutil
import numpy
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')
import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
import pandas as pd
from sendScreenshot import send
from utils import *

#Constants
HEAD_LESS = True # True: won't display the browser and vice versa
#Variables
#--------------------------#
failedSymbols = []
timeframe = ""
symbols = None
dateRange = ""
path = ""
def parseCookieFile(cookiefile):
    cj = cookielib.MozillaCookieJar(cookiefile)
    cj.load()
    cookies =[]
    for c in cj:
        cookies.append({"name":c.name, "value": c.value, "domain": c.domain})
    return cookies

def addIndicator(indicator):
    mySendKey("//div[@data-dialog-name='Indicators']/div/div/input", indicator)
    myClick("//span[@title='{}']".format(indicator))

def shoot(timeframes, symbols, path, isMerged):
    try:
        # Create folder
        if os.path.isdir(path) and isMerged:
            logger.info("Directory already exist: {}".format(path))
            shutil.rmtree(path, ignore_errors=True)
            os.mkdir(path) 
        withChrome(HEAD_LESS)
        url = "https://fialda.com/phan-tich-ky-thuat"
        cookies = parseCookieFile('cookies.txt')
        gotoURL(url, cookies)
        # Close popup video
        myClick("//span[@class='ant-modal-close-x']")
        # Change theme
        myClick("//i[@class='ico-darkmode']")
        # Goto iframe
        switchToIframe("//iframe[contains(@id,'tradingview')]")
        #INCREASE FONT SIZE to 14
        myClick("//div[@id='header-toolbar-properties']")
        # myClick("//div[@data-name='series-properties-dialog']")
        myClick("//div[@data-name='appearance']")
        myClick("//div[@data-name='font-size-select']")
        myClick("//div[@data-name='menu-inner']/div/div/div[text()='14']")
        myClick("//button[@name='submit']")
        # ADD INDICATORS
        myClick("//div[@id='header-toolbar-indicators']")
        addIndicator("MACD")
        addIndicator("Moving Average Exponential")
        addIndicator("Bollinger Bands")
        addIndicator("Relative Strength Index")
        addIndicator("Stochastic")
        myClick("//span[@data-name='close']")

        # FORMAT INDICATOR
        # EMA
        myHoverAndClick("//div[@data-name='legend-source-title'][text()='EMA']")
        myClick("//div[@data-name='legend-source-title'][text()='EMA']/../..//div[@data-name='legend-settings-action']")
        myClick("//div[@data-dialog-name='EMA']//div[text()='Inputs']")
        mySendKey("//div[@data-dialog-name='EMA']//input[@value='9']", "200")
        myClick("//button[@name='submit']")
        for timeframe in timeframes:
            # Change timeframe
            myClick("//div[@id='header-toolbar-intervals']")
            myClick("//div[contains(@class,'menuWrap')]//div[contains(text(),'{}')]".format(timeframe))
            pause(2)
            for symbol in symbols:
                try:
                    mySendKey("//div[@id='header-toolbar-symbol-search']/div/input", symbol)
                    press(Keys.DOWN)
                    press(Keys.RETURN)
                    pause(2)
                    screenShot("{}{}_{}.png".format(path, symbol, timeframe))
                except:
                    logger.info("Failed to screenshot {}".format(symbol))
                    # traceback.print_exc()
            logger.info("Screenshot Fialda successfully on chart {}".format(timeframe))
    except Exception as e:
        logger.error("Failed to screenshot {} {}".format(timeframe, location))
        logger.error(e)
        # traceback.print_exc()
    finally:
        quit()

def shootPsAuto():
    current_time = getCurrentTime()
    if (current_time <= "12:31") or (current_time >= "14:00") or (current_time <= "15:31"):
        stocks = getStocks(os.getenv('ps'))
        location = os.getenv('screenshot_ps_auto')
        shoot(["5 minutes", "15 minutes", "1 hour"], stocks, location, True)

def shootPS():
    stocks = getStocks(os.getenv('ps'))
    location = os.getenv('screenshot_ps')
    shoot(["5 minutes", "15 minutes", "1 hour"], stocks, location, True)

if __name__ == '__main__':
    if (sys.argv[1] == 'daily'):
        shoot(["1 day"], getStocks(os.getenv('all_stocks')), os.getenv('screenshot_1day'), True)
    elif (sys.argv[1] == 'weekly'):
        shoot(["1 week"], getStocks(os.getenv('all_stocks')), os.getenv('screenshot_1week'), True)
    elif (sys.argv[1] == 'monthly'):
        shoot(["1 month"], getStocks(os.getenv('all_stocks')), os.getenv('screenshot_1month'), True)
    elif (sys.argv[1] == '15m'):
        shoot(["15 minutes"], getStocks(os.getenv('following_stocks')) + getStocks(os.getenv('portfolio')), os.getenv('screenshot_15min'), True)
        if (len(sys.argv) == 3):
            send("15 minutes", os.getenv('screenshot_15min'))
    elif (sys.argv[1] == '1h'):
        shoot(["1 hour"], getStocks(os.getenv('following_stocks')) + getStocks(os.getenv('portfolio')), os.getenv('screenshot_1h'), True)
        if (len(sys.argv) == 3):
            send("1 hour", os.getenv('screenshot_1h'))
    elif (sys.argv[1] == '1d'):
        shoot(["1 day"], getStocks(os.getenv('following_stocks')) + getStocks(os.getenv('portfolio')), os.getenv('screenshot_realtime_1day'), True)
        if (len(sys.argv) == 3):
            send("1 day", os.getenv('screenshot_realtime_1day'))
    elif (sys.argv[1] == 'ps_auto'):
        logger.info("PS Auto")
        shootPsAuto()
        if (len(sys.argv) == 3):
            send("ps", os.getenv('screenshot_ps_auto'))
    elif (sys.argv[1] == 'ps'):
        logger.info("PS")
        shootPS()
        if (len(sys.argv) == 3):
            send("ps", os.getenv('screenshot_ps'))
    else:
        if (sys.argv[1] == 'portfolio'):
            stocks = getStocks(os.getenv('portfolio'))
            location = os.getenv('screenshot_portfolio')
            logger.info("Portfolio")
        elif (sys.argv[1] == 'following'):
            stocks = getStocks(os.getenv('following_stocks'))
            location = os.getenv('screenshot_following')
            logger.info("Following")
        elif (sys.argv[1] == 'vn30'):
            stocks = getStocks(os.getenv('vn30'))
            location = os.getenv('screenshot_vn30')
            logger.info("VN30")
        elif (sys.argv[1] == 'uptrends'):
            stocks = getStocks(os.getenv('uptrend_stocks'))
            location = os.getenv('screenshot_uptrend')
            logger.info("trends")
        elif (sys.argv[1] == 'ducky'):
            stocks = getStocks(os.getenv('ducky_stocks'))
            location = os.getenv('screenshot_ducky')
            logger.info("scan")
        elif (sys.argv[1] == 'potential'):
            stocks = getStocks(os.getenv('potential_stocks'))
            location = os.getenv('screenshot_potential')
            logger.info("scan")
        elif (sys.argv[1] == 'sideway'):
            stocks = getStocks(os.getenv('sideway_stocks'))
            location = os.getenv('screenshot_sideway')
            logger.info("Sideway")
        elif (sys.argv[1] == 'target'):
            stocks = getStocks(os.getenv('target'))
            location = os.getenv('screenshot_target')
            logger.info("Target")
        elif (sys.argv[1] == 'softzones'):
            stocks = getStocks(os.getenv('soft_zone_stocks'))
            location = os.getenv('screenshot_soft_zones')
            logger.info("scan")
        elif (sys.argv[1] == 'urgent'):
            stocks = getStocks(os.getenv('urgent'))
            location = os.getenv('screenshot_urgent')
            logger.info("urgent")
        else:
            logger.info("List of stocks")
            stocks = sys.argv[1].split(",")
            location = os.getenv('screenshot_urgent')
        shoot(["1 day", '1 hour'], stocks, location, True)
        # shoot(["1 hour"], stocks, location, True)
        # shoot(["1 day"], stocks, location, True)
        if (len(sys.argv) == 3):
            send(sys.argv[1], location)