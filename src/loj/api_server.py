import json
import os
import subprocess
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from loj.tools.wallet_tools import check_position
import random
from loj.tools.wallet_tools import check_position, load_positions

app = FastAPI(title="Lean Alpha Multi-Asset Gateway")

API_KEY_NAME = "X-Agent-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
AGENT_SECRET = os.getenv("VIRTUALS_API_KEY", "lojer_secret_123")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != AGENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Secret Key")
    return api_key

class TradeRequest(BaseModel):
    ticker: str = "BTC"
    market_type: str = "CEX"

# دقیقاً همان ۲ ارزی که می‌خواستی
TARGET_ASSETS = ["BTC", "ETH"]

@app.get("/status")
def get_status():
    """مشاهده وضعیت پوزیشن‌ها"""
    if os.path.exists("open_positions.json"):
        with open("open_positions.json", "r") as f:
            return json.load(f)
    return {"message": "No active positions in memory."}

@app.post("/run-analysis")
def trigger_agent_pipeline(request: TradeRequest, api_key: str = Security(verify_api_key)):
    """اتصال انفرادی برای زمان‌هایی که دستی یا از طرف ویرچوالز صدا زده می‌شود"""
    try:
        cmd = ["python", "-m", "loj.main", "--ticker", request.ticker, "--type", "CEX"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if os.path.exists("signal.json"):
            with open("signal.json", "r") as f:
                signal_data = json.load(f)
            return {
                "status": "success",
                "execution_log": result.stdout,
                "payload": signal_data
            }
        else:
            return {"status": "skipped_or_no_signal", "log": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {e.stderr}")

@app.post("/run-all-assets")
def trigger_full_scan(api_key: str = Security(verify_api_key)):
    """اسکن چرخشی عادلانه با رعایت محدودیت باجت"""
    
    # قانون ۱: آیا کلاً پوزیشن بازی در سیستم داریم؟ (جلوگیری از ارور کمبود مارجین)
    positions = load_positions()
    for asset, data in positions.items():
        # همزمان تایم‌استاپ را هم چک می‌کنیم که اگر وقتش گذشته، اول بسته‌شود
        status = check_position(asset) 
        if status == "OPEN":
            return {
                "status": "SKIPPED", 
                "message": f"Global Limit: Currently holding an open position on {asset}."
            }

    # قانون ۲: بُر زدن لیست ارزها برای عدالت
    assets_to_scan = TARGET_ASSETS.copy()
    random.shuffle(assets_to_scan)
    
    summary = {}
    for count, asset in enumerate(assets_to_scan):
        ticker = f"{asset}USDT"
        print(f"🔍 System scanning target {count+1}/{len(assets_to_scan)}: {ticker}")
        
        try:
            cmd = ["python", "-m", "loj.main", "--ticker", ticker, "--type", "CEX"]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            summary[asset] = "SCAN_COMPLETED"
            
            # قانون ۳: اگر در همین اسکن، ربات پوزیشنی باز کرد، اسکن ارز بعدی را متوقف کن
            if check_position(asset) == "OPEN":
                summary["system_message"] = f"Budget locked for {asset}. Halting further scans."
                break
                
        except subprocess.CalledProcessError as e:
            summary[asset] = f"FAILED: {e.stderr}"
            
    return {
        "status": "scan_finished",
        "results": summary
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)