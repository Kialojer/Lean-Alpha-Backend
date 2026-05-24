import json
import os
from pickle import FALSE
import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from datetime import datetime, timedelta

POSITIONS_FILE = "open_positions.json"

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def save_positions(positions):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def check_position(asset: str) -> str:
    positions = load_positions()
    if asset in positions and positions[asset]["status"] == "OPEN":
        opened_at = datetime.fromisoformat(positions[asset]["opened_at"])
        if datetime.now() - opened_at > timedelta(hours=48):
            print(f"⏰ [TIME STOP] Position for {asset} open for >72h. Closing.")
            close_position(asset, paper_trading=False) # زمان اجرای واقعی روی Mainnet این را False کن
            return "CLOSED_DUE_TO_TIME"
        return "OPEN"
    return "NONE"

def close_position(asset: str, paper_trading: bool = True):
    positions = load_positions()
    if asset in positions:
        if not paper_trading:
            try:
                # کدهای بستن پوزیشن واقعی روی بازار فیوچرز هایپرلیکویید
                secret_key = os.getenv("HL_PRIVATE_KEY")
                account: LocalAccount = eth_account.Account.from_key(secret_key)
                exchange = Exchange(account, constants.MAINNET_API_URL, account_addr=account.address)
                # بستن پوزیشن مارکت با حجم معکوس
                is_buy = True if positions[asset]["action"] == "SELL" else False
                exchange.market_open(asset, is_buy, positions[asset]["size"], None, None)
            except Exception as e:
                print(f"⚠️ Could not execute real close on Hyperliquid: {e}")
        
        positions[asset]["status"] = "CLOSED"
        positions[asset]["closed_at"] = datetime.now().isoformat()
        save_positions(positions)
        print(f"🔒 Position for {asset} marked as CLOSED.")

def execute_signal(signal_file_path: str = "signal.json", paper_trading: bool = True):
    """اجرای سیگنال روی شبکه اصلی (Mainnet) یا شبیه‌ساز"""
    try:
        with open(signal_file_path, "r") as f:
            signal = json.load(f)

        asset = signal["asset"].replace("USDT", "")
        action = signal["action"]
        leverage = signal["leverage"]

        if action == "HOLD":
            return {"status": "HOLD", "message": "Signal is HOLD."}

        # محاسبه حجم بر اساس باجت ۲۰ دلاری و لوریج
        # برای شروع از کمترین حجم مجاز صرافی استفاده می‌کنیم
        sz = 0.0001 if asset == "BTC" else (0.001 if asset == "ETH" else 1.0)

        if paper_trading:
            print(f"🟢 [SIMULATION] {action} {asset} {leverage}x")
        else:
            # 🚨 اتصال به شبکه اصلی هایپرلیکویید با پول واقعی
            secret_key = os.getenv("HL_PRIVATE_KEY")
            if not secret_key: raise ValueError("HL_PRIVATE_KEY missing!")
            
            account: LocalAccount = eth_account.Account.from_key(secret_key)
            exchange = Exchange(account, constants.MAINNET_API_URL, account_addr=account.address)
            
            # ۱. تنظیم لوریج در صرافی واقعی
            exchange.update_leverage(leverage, asset)
            # ۲. ثبت سفارش مارکت واقعی
            is_buy = True if action == "BUY" else False
            exchange.market_open(asset, is_buy, sz, None, signal["current_price"])

        # ذخیره در حافظه ربات
        positions = load_positions()
        positions[asset] = {
            "status": "OPEN",
            "action": action,
            "entry_price": signal["current_price"],
            "opened_at": datetime.now().isoformat(),
            "leverage": leverage,
            "size": sz
        }
        save_positions(positions)
        return {"status": "OPENED", "asset": asset, "action": action}

    except Exception as e:
        print(f"❌ Wallet Error: {str(e)}")
        return {"status": "ERROR", "message": str(e)}