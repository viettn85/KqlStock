import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import glob
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')
import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
import traceback

def send(timeframe, location):
    try:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H-%M")
        subject = "Update {} at {} ".format(timeframe, current_time)
        body = "Your screenshots. Happy Trading!"

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["Subject"] = subject

        # Add body to email
        message.attach(MIMEText(body, "plain"))
        csvFiles = list(filter(lambda x: os.path.splitext(x)
                                [1], os.listdir(location)))
        for filename in csvFiles:
            filename = location + filename
            # Open PDF file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(os.getenv('sender'), os.getenv('password'))
            server.sendmail(os.getenv('sender'), os.getenv('receiver').split(','), message.as_string())
        logger.info("Sent {} from {}".format(subject, location))
    except:
        logger.error("Failed to send email {} from {}".format(subject, location))
        traceback.print_exc()
if __name__ == '__main__':
    send(os.getenv('screenshot_15min'))
