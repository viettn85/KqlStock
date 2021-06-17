from datetime import datetime
import pandas as pd
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback, os, logging

import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')

def getCurrentTime():
    now = datetime.now()
    return str(now.strftime("%H:%M"))

def getStocks(stockFile):
    return list(pd.read_csv(stockFile, header=None)[0])

def sendEmail(subject, text):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H-%M")
    try:
        subject = "{} - {}".format(subject, current_time)
        body = text
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
        logger.info("Sent {}".format(subject))
    except:
        logger.error("Failed to send email to notify qualified stocks {}".format(current_time))
        traceback.print_exc()