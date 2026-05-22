import json
import os
from datetime import datetime, timedelta

# مسیر ذخیره حافظه ربات
POSITIONS_FILE = "open_positions.json"

def load_positions():
    """خواندن حافظه از فایل JSON"""
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_positions(positions):
    """ذخیره حافظه جدید در فایل JSON"""
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def check_position(asset: str) -> str:
    """بررسی می‌کند که آیا پوزیشنی باز است یا خیر و Time Stop را اعمال می‌کند"""
    positions = load_positions()
    if asset in positions and positions[asset]["status"] == "OPEN":
        # بررسی Time Stop (مثلاً اگر ۴۸ ساعت گذشته باشد)
        opened_at = datetime.fromisoformat(positions[asset]["opened_at"])
        if datetime.now() - opened_at > timedelta(hours=48):
            print(f"⏰ [TIME STOP] Position for {asset} has been open for >48h. Closing to save funding fees.")
            close_position(asset)
            return "CLOSED_DUE_TO_TIME"
        return "OPEN"
    return "NONE"

def close_position(asset: str):
    """بستن یک پوزیشن در حافظه"""
    positions = load_positions()
    if asset in positions:
        positions[asset]["status"] = "CLOSED"
        positions[asset]["closed_at"] = datetime.now().isoformat()
        save_positions(positions)
        print(f"🔒 Position for {asset} marked as CLOSED in memory.")

def execute_signal(signal_file_path: str = "signal.json", paper_trading: bool = True):
    """اجرای سیگنال و ثبت آن در حافظه"""
    print("\n🔌 Initializing Execution Module...")
    try:
        with open(signal_file_path, "r") as f:
            signal = json.load(f)

        asset = signal["asset"].replace("USDT", "")
        action = signal["action"]
        leverage = signal["leverage"]

        if action == "HOLD":
            print("⏸️ Signal is HOLD. No trade executed. Memory unchanged.")
            return

        sz = 0.001 if asset == "BTC" else 0.1

        if paper_trading:
            print("="*45)
            print("🟢 [PAPER TRADING MODE - SIMULATION]")
            print(f"Action: {action} | Asset: {asset} | Leverage: {leverage}x")
            print(f"Size: {sz} | Entry: ${signal['current_price']}")
            print(f"Stop Loss: ${signal['stop_loss']} | Take Profit: ${signal['take_profit']}")
            print("="*45)
            print("✅ Simulated Trade Executed Successfully.")

            # ثبت در حافظه به عنوان پوزیشن باز
            positions = load_positions()
            positions[asset] = {
                "status": "OPEN",
                "action": action,
                "entry_price": signal["current_price"],
                "opened_at": datetime.now().isoformat(),
                "leverage": leverage,
                "stop_loss": signal["stop_loss"],
                "take_profit": signal["take_profit"]
            }
            save_positions(positions)
            print(f"💾 Memory Updated: {asset} is now secured as OPEN.")

    except FileNotFoundError:
        print("❌ Error: signal.json not found.")

if __name__ == "__main__":
    execute_signal("../../signal.json", paper_trading=True)