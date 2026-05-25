import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import yfinance as yf

def get_defillama_data(protocol_name: str = "polygon"):
    try:
        url = "https://api.llama.fi/v2/chains"
        res = requests.get(url).json()

        chain_data = next(
            (item for item in res if item["name"].lower() == protocol_name.lower()),
            None
        )

        if chain_data:
            return {
                "Chain": chain_data.get("name"),
                "TVL": chain_data.get("tvl")
            }

        return {"Error": "Chain/Protocol not found"}

    except Exception as e:
        return {"Error": str(e)}

def get_dex_data(identifier: str):
    """Fetches decentralized token data using DexScreener via Search Endpoint."""
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={identifier}"
        res = requests.get(url).json()

        if res.get("pairs") and len(res["pairs"]) > 0:
            best_pair = res["pairs"][0]

            return {
                "network": best_pair.get("chainId"),
                "dex": best_pair.get("dexId"),
                "price_usd": best_pair.get("priceUsd"),
                "liquidity_usd": best_pair.get("liquidity", {}).get("usd"),
                "volume_24h": best_pair.get("volume", {}).get("h24"),
                "price_change_24h": best_pair.get("priceChange", {}).get("h24")
            }

        return {"Error": f"No DEX pairs found for {identifier}"}

    except Exception as e:
        return {"Error": str(e)}

def get_offchain_data(symbol: str):
    """Fetches Off-Chain Derivatives data (Funding Rate & Open Interest) from Binance."""
    try:
        # Fetch Funding Rate
        fr_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
        fr_res = requests.get(fr_url).json()
        funding_rate = float(fr_res.get('lastFundingRate', 0)) * 100  # Convert to Percentage
        
        # Fetch Open Interest
        oi_url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
        oi_res = requests.get(oi_url).json()
        open_interest = float(oi_res.get('openInterest', 0))
        
        return {
            "Funding_Rate_Pct": round(funding_rate, 4),
            "Open_Interest_Tokens": open_interest
        }
    except Exception:
        return {"Notice": "Off-chain Futures data not available for this asset."}

def get_technical_data(symbol: str = "BTCUSDT", is_dex: bool = False):
    if is_dex:
        return {
            "Notice": "Technical indicators skipped for DEX token."
        }

    try:
        url = (
            f"https://api.binance.com/api/v3/klines"
            f"?symbol={symbol}&interval=1d&limit=100"
        )

        res = requests.get(url).json()

        df = pd.DataFrame(
            res,
            columns=[
                'time', 'open', 'high', 'low', 'close',
                'vol', 'close_time', 'qav',
                'nat', 'tbbav', 'tbqav', 'ignore'
            ]
        )

        df['close'] = df['close'].astype(float)

        # RSI
        rsi = RSIIndicator(close=df['close'], window=14)
        df['RSI_14'] = rsi.rsi()

        # MACD
        macd = MACD(close=df['close'])

        df['MACD'] = macd.macd()
        df['MACD_SIGNAL'] = macd.macd_signal()
        df['MACD_HIST'] = macd.macd_diff()

        latest = df.iloc[-1]

        return {
            "price": round(latest['close'], 2),
            "RSI_14": round(latest['RSI_14'], 2),
            "MACD_Histogram": round(latest['MACD_HIST'], 2)
        }

    except Exception as e:
        return {
            "Error": str(e)
        }

def get_sentiment_data():
    try:
        url = "https://api.alternative.me/fng/"
        res = requests.get(url).json()

        return {
            "value": int(res['data'][0]['value']),
            "classification": res['data'][0]['value_classification']
        }

    except:
        return {
            "value": 50,
            "classification": "Neutral (Fallback)"
        }

def get_macro_data():
    try:
        dxy = yf.Ticker("DX-Y.NYB")
        hist = dxy.history(period="5d")

        trend = (
            "Up"
            if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]
            else "Down"
        )

        return {"DXY_Trend": trend}

    except:
        return {"DXY_Trend": "Unknown"}

def build_market_payload(
    identifier: str,
    asset_type: str = "CEX",
    protocol_name: str = None
):
    print(f"\n⚙️ Fetching Live Data for {identifier} ({asset_type})...")

    payload = {
        "Sentiment": get_sentiment_data(),
        "Macro": get_macro_data(),
    }

    if asset_type == "CEX":
        
        payload["Technical"] = get_technical_data(
            identifier,
            is_dex=False
        )
        payload["Off_Chain_Futures"] = get_offchain_data(identifier)

    elif asset_type == "DEX":
        payload["DEX_Data"] = get_dex_data(identifier)

    if protocol_name:
        payload["On_Chain_TVL"] = get_defillama_data(protocol_name)

    return payload
