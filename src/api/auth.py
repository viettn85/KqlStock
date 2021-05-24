import os
import sys 
import requests
import logging
import logging.config
import pandas as pd
from datetime import datetime
import random
from dotenv import set_key
from dotenv import load_dotenv
# load_dotenv(dotenv_path='stock.env')

if __name__ == '__main__':
    print("Authenticating with KEY and PIN")
    print(len(sys.argv))
    if len(sys.argv) == 3: # auth.py KEY PIN
        set_key('stock.env', "pKeyAuthenticate", sys.argv[1], quote_mode='never')
        os.environ["pKeyAuthenticate"] = sys.argv[1]
        set_key('stock.env', "PIN", sys.argv[2], quote_mode='never')
        os.environ["PIN"] = sys.argv[2]
        print("Authenticated")
    elif len(sys.argv) == 4: # auth.py future KEY PIN
        set_key('future.env', "pinf", sys.argv[2], quote_mode='never')
        os.environ["pinf"] = sys.argv[1]
        set_key('future.env', "cookief", sys.argv[3], quote_mode='never')
        os.environ["cookief"] = sys.argv[3]
        print("Authenticated")
    else:
        print("Bad Request")
