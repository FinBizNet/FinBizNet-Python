from SmartApi.smartConnect import SmartConnect  # Connect to Angel One SmartAPI
from config.settings import load_keys           # Load API credentials
from utils.totp import get_totp_token           # Generate TOTP for login
from functools import lru_cache

keys = load_keys()

_cached_obj = None

def get_api_object():
    global _cached_obj
    if _cached_obj is None:
        obj = SmartConnect(api_key=keys["API_KEY"])
        token = get_totp_token(keys["QR_CODE_KEY"])
        obj.generateSession(keys["USERNAME"], keys["PASSWORD"], token)
        _cached_obj = obj
    return _cached_obj


@lru_cache(maxsize=1000)  # ✅ Cache up to 1000 unique searches to reduce API load
def search_scrip_and_extract(search_str, exchange):
    print(f"🔍 Searching for scrip: {search_str} on {exchange}")
    obj = get_api_object()

    try:
        result = obj.searchScrip(exchange, search_str)
        print("📦 Raw search result:", result)
    except Exception as e:
        print("❌ Exception from SmartAPI searchScrip:", str(e))
        raise e

    if not result or 'data' not in result or not result['data']:
        raise ValueError("No matching scrip found")

    # ✅ Filter only -EQ instruments
    scrip_data = next(
        (item for item in result['data'] if item['tradingsymbol'].endswith('-EQ')),
        None
    )

    if not scrip_data:
        raise ValueError("Matching EQ tradingsymbol not found in search results.")

    return {
        "exchange": scrip_data["exchange"],
        "tradingsymbol": scrip_data["tradingsymbol"],
        "symboltoken": scrip_data["symboltoken"]
    }





# Fetch LTP
def fetch_ltp(exchange, tradingsymbol, symboltoken):
    obj = get_api_object()
    return obj.ltpData(exchange=exchange, tradingsymbol=tradingsymbol, symboltoken=symboltoken)

# Fetch Candlestick Data
def fetch_candle_data(exchange, symboltoken, interval, from_date, to_date):
    obj = get_api_object()
    return obj.getCandleData(
        exchange=exchange,
        symboltoken=symboltoken,
        interval=interval,
        fromdate=from_date,
        todate=to_date
    )

# Fetch Security Info
def fetch_security_info(exchange, tradingsymbol, symboltoken):
    obj = get_api_object()
    return obj.getSecurityInfo(
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        symboltoken=symboltoken
    )

# Fetch Market Data
def fetch_market_data(exchange, tradingsymbol, symboltoken):
    obj = get_api_object()
    return obj.getMarketData(
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        symboltoken=symboltoken
    )

# Fetch Option Chain
def fetch_option_chain(exchange, tradingsymbol, symboltoken):
    obj = get_api_object()
    return obj.getOptionChain(
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        symboltoken=symboltoken
    )

# Fetch Expiry List
def fetch_expiry_list(exchange, tradingsymbol, symboltoken):
    obj = get_api_object()
    return obj.getExpiryList(
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        symboltoken=symboltoken
    )

# Fetch Master Contract (no symboltoken needed)
def fetch_master_contract(exchange):
    obj = get_api_object()
    return obj.getMasterContract(exchange=exchange)
