from SmartApi.smartConnect import SmartConnect  # Connect to Angel One SmartAPI
from config.settings import load_keys           # Load API credentials
from utils.totp import get_totp_token           # Generate TOTP for login
from functools import lru_cache
from datetime import datetime

keys = load_keys()

_cached_obj = None
_cached_time = None   # <-- new variable

def get_api_object(force_renew=False):
    global _cached_obj, _cached_time

    # Refresh if forced, never logged in, or older than 20 minutes
    if force_renew or _cached_obj is None or (_cached_time and (datetime.now() - _cached_time).total_seconds() > 1200):
        try:
            obj = SmartConnect(api_key=keys["API_KEY"])
            token = get_totp_token(keys["QR_CODE_KEY"])
            login_response = obj.generateSession(keys["USERNAME"], keys["PASSWORD"], token)

            if not isinstance(login_response, dict) or "data" not in login_response:
                raise ValueError("Login failed or malformed response.")

            _cached_obj = obj
            _cached_time = datetime.now()  # ✅ store login time
            print(f"🔑 Token refreshed at {_cached_time}")

        except Exception as e:
            print(f"❌ Error during login: {e}")
            _cached_obj = None
            _cached_time = None
            raise e

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
    try:
        obj = get_api_object()
        return obj.ltpData(exchange=exchange, tradingsymbol=tradingsymbol, symboltoken=symboltoken)
    except Exception as e:
        if "Invalid Token" in str(e):
            print("🔁 Token expired. Re-authenticating...")
            obj = get_api_object(force_renew=True)
            return obj.ltpData(exchange=exchange, tradingsymbol=tradingsymbol, symboltoken=symboltoken)
        raise e



# services/smartapi_service.py
from functools import lru_cache

@lru_cache(maxsize=512)
def resolve_symboltoken(tradingsymbol: str, exchange: str = "NSE") -> str:
    """
    Look up the latest symboltoken for a given tradingsymbol+exchange.
    Cached for the life of the process to avoid rate limits.
    """
    print(f"🔍 Resolving token for {exchange}:{tradingsymbol} (cache MISS)")

    scrip = search_scrip_and_extract(tradingsymbol, exchange)
    token = scrip.get("symboltoken")

    if not token:
        raise ValueError(f"Could not resolve symboltoken for {exchange}:{tradingsymbol}")

    print(f"✅ Token resolved for {exchange}:{tradingsymbol} → {token}")
    return str(token)



# Fetch Candlestick Data
def fetch_candle_data(exchange, symboltoken, interval, from_date, to_date):
    try:
        obj = get_api_object()
        return obj.getCandleData(
            exchange=exchange,
            symboltoken=symboltoken,
            interval=interval,
            fromdate=from_date,
            todate=to_date
        )
    except Exception as e:
        if "Invalid Token" in str(e):
            print("🔁 Token expired. Re-authenticating...")
            obj = get_api_object(force_renew=True)
            return obj.getCandleData(
                exchange=exchange,
                symboltoken=symboltoken,
                interval=interval,
                fromdate=from_date,
                todate=to_date
            )
        raise e


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
    params = {
        "tradingsymbol": tradingsymbol,
        "symboltoken": symboltoken
    }
    return obj.getMarketData(params)



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
