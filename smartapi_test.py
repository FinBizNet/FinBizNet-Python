from SmartApi.smartConnect import SmartConnect
import pyotp
import os
from datetime import date, timedelta, datetime
import time
import pandas as pd
import sys
import requests
import math
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)  # Ignore user warnings

# 🔑 Read secrets from a file
with open("key_secret.txt", "r") as f:
    key_secret = [line.strip() for line in f.readlines()]

# 🔐 Extract credentials
api_key = key_secret[0]
client_id = key_secret[1]
username = key_secret[2]
password = key_secret[3]
qr_code_key = key_secret[4]

# 🧠 Initialize API client
obj = SmartConnect(api_key=api_key)

# 🕑 Generate TOTP
totp = pyotp.TOTP(qr_code_key).now()

# 🔐 Login
data = obj.generateSession(username, password, totp)

# 📈 Get RMS Limits (balance)
limits = obj.rmsLimit()
print("💰 RMS Limits:", limits)

# 📉 Get LTP of RELIANCE
ltp = obj.ltpData(
    exchange="NSE",              # Exchange: NSE or BSE
    tradingsymbol="RELIANCE-EQ",  # Trading symbol (must be exact)
    symboltoken="2885"            # Token ID for RELIANCE (from symbol dump)
)

print("💹 LTP Data:", ltp)
