import argparse
import json
import os
from loj.crew import TradingSystem
# ایمپورت کردن ماژول حافظه و اجرا
from loj.tools.wallet_tools import check_position, execute_signal 

def run():
    parser = argparse.ArgumentParser(description="Autonomous Hyperliquid Trading Agent")
    parser.add_argument("--ticker", type=str, default="BTCUSDT", help="Target coin")
    parser.add_argument("--type", type=str, default="CEX", choices=["CEX", "DEX"], help="Market type")
    parser.add_argument("--protocol", type=str, default=None, help="Protocol name if DEX")
    
    args = parser.parse_args()
    identifier = args.ticker.upper()
    
    if args.type == "CEX" and not identifier.endswith("USDT"):
        identifier += "USDT"

    asset_pure = identifier.replace("USDT", "")

    print(f"🤖 [AUTO-MODE] Initiating sequence for {identifier} on {args.type}...")
    
    # 🚨 ۱. بررسی حافظه قبل از هر کاری
    status = check_position(asset_pure)
    if status == "OPEN":
        print(f"🛡️ [RISK MANAGER] We already have an OPEN position for {asset_pure}.")
        print("🛑 Skipping AI analysis to prevent over-trading and duplicate fees.")
        return  # خروج کامل از برنامه، ایجنت‌ها بیدار نمی‌شوند!

    # ۲. اگر پوزیشنی باز نبود، هوش مصنوعی را بیدار کن
    system = TradingSystem()
    result = system.run_pipeline(
        identifier=identifier,
        asset_type=args.type,
        protocol_name=args.protocol
    )

    if result and "signal" in result:
        output_file = "signal.json"
        try:
            signal_dict = json.loads(result["signal"])
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(signal_dict, f, indent=4)
            print(f"\n✅ [SUCCESS] AI Signal saved to {output_file}")
            
        except json.JSONDecodeError:
            print("\n[WARNING] Could not parse JSON. Saving raw text...")
            with open("signal_raw.txt", "w", encoding="utf-8") as f:
                f.write(result["signal"])
            return

        print("\n" + "="*50)
        print("🚀 SOCIAL MEDIA PAYLOAD (X):")
        print("="*50)
        print(result["tweet"])
        
        # 🚨 ۳. ارسال سیگنال به ماژول ترید و ذخیره در حافظه
        execute_signal(output_file, paper_trading=True)
        
    else:
        print("❌ [ERROR] Pipeline execution failed.")

if __name__ == "__main__":
    run()