import sys
sys.path.insert(1, 'src/api')
from stock import getSecurityList
import os
import pandas as pd
from datetime import datetime
import traceback
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
today = datetime.today().strftime("%Y-%m-%d")

def getTargetPrices():
    return pd.read_csv(os.getenv('tracking'))

def getCurrentPrices(stocks):
    return getSecurityList(stocks)[['Stock', 'Price']]

def getQualifiedPrices(targetPrices, currentPrices):
    currentPrices.Price = currentPrices.Price / 100
    finalDf = pd.merge(targetPrices, currentPrices, on="Stock")
    finalDf = finalDf[["Stock", "Target", "Price", "Qualified"]]
    finalDf.Qualified = finalDf.Target <= finalDf.Price
    logger.info(finalDf)
    qualifiedDf = finalDf[finalDf.Qualified]
    return qualifiedDf

def sendEmail(qualifiedPrices):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H-%M")
    try:
        subject = "Qualified Stock {}".format(current_time)
        body = str(qualifiedPrices)
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["Subject"] = subject

        # Add body to email
        message.attach(MIMEText(body, "plain"))
        # message.attach(qualifiedPrices)
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(os.getenv('sender'), os.getenv('password'))
            server.sendmail(os.getenv('sender'), os.getenv('receiver').split(','), message.as_string())
        logger.info("Sent qualified stocks")
    except:
        logger.error("Failed to send email to notify qualified stocks {}".format(current_time))
        traceback.print_exc()

if __name__ == '__main__':
    targetPrices = getTargetPrices()
    currentPrices = getCurrentPrices(list(targetPrices['Stock']))
    qualifiedPrices = getQualifiedPrices(targetPrices, currentPrices)
    if len(qualifiedPrices) > 0:
        sendEmail(qualifiedPrices)