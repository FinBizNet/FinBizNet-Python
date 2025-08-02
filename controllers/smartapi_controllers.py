from flask import request, jsonify
from services.smartapi_service import (
    search_scrip_and_extract,
    fetch_ltp,
    get_api_object
)
from datetime import datetime, timedelta
import time

def get_candle_data(exchange, tradingsymbol, symboltoken, interval="ONE_DAY", days=250):
    obj = get_api_object()

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    try:
        params = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "interval": interval,
            "fromdate": from_date.strftime('%Y-%m-%d %H:%M'),
            "todate": to_date.strftime('%Y-%m-%d %H:%M')
        }

        candles = obj.getCandleData(params)
        if not candles or "data" not in candles:
            raise ValueError("No candle data received")

        parsed = [
            {
                "datetime": c[0],
                "open": c[1],
                "high": c[2],
                "low": c[3],
                "close": c[4],
                "volume": c[5]
            }
            for c in candles["data"]
        ]
        return parsed

    except Exception as e:
        print("❌ Error in get_candle_data:", str(e))
        raise e


def combined_data():
    try:
        search_str = request.args.get('search_str')
        exchange = request.args.get('exchange')

        # 1. Get scrip data
        scrip = search_scrip_and_extract(search_str, exchange)
        tradingsymbol = scrip.get("tradingsymbol")
        symboltoken = scrip.get("symboltoken")

        # 2. LTP data
        ltp_data = fetch_ltp(exchange, tradingsymbol, symboltoken)

        # 3. Candles
        candle_data = get_candle_data(exchange, tradingsymbol, symboltoken)
        closes = [c['close'] for c in candle_data]

        # 4. Moving Averages
        dma_5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else None
        dma_30 = sum(closes[-30:]) / 30 if len(closes) >= 30 else None
        dma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        dma_200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None

        # 5. Returns
        def calc_return(days):
            if len(candle_data) < days:
                return None
            past_close = candle_data[-days]['close']
            current = candle_data[-1]['close']
            return round((current - past_close) / past_close * 100, 2) if past_close != 0 else None

        # 6. Add calculated values
        ltp_data.update({
            "DMA_5": dma_5,
            "DMA_30": dma_30,
            "DMA_50": dma_50,
            "DMA_200": dma_200,
            "1D%": calc_return(1),
            "5D%": calc_return(5),
            "30D%": calc_return(30),
            "1Y%": calc_return(250),
            "52W-High": max(c['high'] for c in candle_data),
            "52W-Low": min(c['low'] for c in candle_data),
        })

        # ✅ 7. Add extra useful data from scrip (only useful keys)
        extra_info = {
            "symboltoken": scrip.get("symboltoken"),
            "tradingsymbol": scrip.get("tradingsymbol"),
            "exchange": scrip.get("exchange"),
            "name": scrip.get("name"),
            "instrumenttype": scrip.get("instrumenttype"),
            "lotsize": scrip.get("lotsize"),
            "ticksize": scrip.get("ticksize"),
            "expiry": scrip.get("expiry"),
            "strikeprice": scrip.get("strikeprice"),
            "optiontype": scrip.get("optiontype"),
            "isin": scrip.get("isin"),
        }
        ltp_data.update(extra_info)

        # ✅ 8. Add latest candle snapshot (for frontend highlights)
        latest_candle = candle_data[-1] if candle_data else {}
        ltp_data["latest_candle"] = latest_candle

        return jsonify(ltp_data)

    except Exception as e:
        print("❌ Error in combined_data:", str(e))
        return jsonify({"error": str(e)}), 400


WATCHLIST = [
    {"name": "RELIANCE", "exchange": "NSE", "tradingsymbol": "RELIANCE-EQ", "symboltoken": "2885"},
    {"name": "TCS", "exchange": "NSE", "tradingsymbol": "TCS-EQ", "symboltoken": "11536"},
    {"name": "HDFCBANK", "exchange": "NSE", "tradingsymbol": "HDFCBANK-EQ", "symboltoken": "1333"},
    {"name": "INFY", "exchange": "NSE", "tradingsymbol": "INFY-EQ", "symboltoken": "1594"},
    {"name": "ICICIBANK", "exchange": "NSE", "tradingsymbol": "ICICIBANK-EQ", "symboltoken": "4963"},
    {"name": "TATAMOTORS", "exchange": "NSE", "tradingsymbol": "TATAMOTORS-EQ", "symboltoken": "3456"},
    {"name": "BHARTIARTL", "exchange": "NSE", "tradingsymbol": "BHARTIARTL-EQ", "symboltoken": "10604"},
    {"name": "MARUTI", "exchange": "NSE", "tradingsymbol": "MARUTI-EQ", "symboltoken": "10999"},
    {"name": "ITC", "exchange": "NSE", "tradingsymbol": "ITC-EQ", "symboltoken": "1660"},
    {"name": "KOTAKBANK", "exchange": "NSE", "tradingsymbol": "KOTAKBANK-EQ", "symboltoken": "10847"},
    {"name": "SBIN", "exchange": "NSE", "tradingsymbol": "SBIN-EQ", "symboltoken": "3045"},
    {"name": "HCLTECH", "exchange": "NSE", "tradingsymbol": "HCLTECH-EQ", "symboltoken": "7229"},
    {"name": "AXISBANK", "exchange": "NSE", "tradingsymbol": "AXISBANK-EQ", "symboltoken": "212"},
    {"name": "SUNPHARMA", "exchange": "NSE", "tradingsymbol": "SUNPHARMA-EQ", "symboltoken": "1348"},
    {"name": "LT", "exchange": "NSE", "tradingsymbol": "LT-EQ", "symboltoken": "11483"},
]

def ticker_data():
    stocks = []
    for stock in WATCHLIST:
        try:
            ltp_response = fetch_ltp(
                exchange=stock["exchange"],
                tradingsymbol=stock["tradingsymbol"],
                symboltoken=stock["symboltoken"]
            )
            ltp_data = ltp_response.get("data", {})

            ltp = float(ltp_data.get("ltp", 0))
            close = float(ltp_data.get("close", 1))  # Avoid division by zero

            change_percent = ((ltp - close) / close * 100) if close != 0 else 0

            stocks.append({
                "name": stock["name"],
                "ltp": round(ltp, 2),
                "changePercent": round(change_percent, 2)
            })

        except Exception as e:
            print(f"❌ Error fetching {stock['name']}: {e}")
            continue
    return jsonify(stocks)






# ❌ UNUSED ROUTES - COMMENTED OUT TO AVOID EXECUTION, RETAINED FOR FUTURE USE

"""
# def search_scrip():
#     ...

# def ltp():
#     ...

# def candle_data():
#     ...

# def stock_data():
#     ...

# def security_info():
#     ...

# def market_data():
#     ...

# def option_chain():
#     ...

# def expiry_list():
#     ...

# def master_contract():
#     ...
"""
