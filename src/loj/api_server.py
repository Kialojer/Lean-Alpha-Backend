from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
import json
import os
import subprocess
from pydantic import BaseModel
from loj.tools.wallet_tools import check_position

app = FastAPI(title="Lean Alpha Multi-Asset Gateway")

API_KEY_NAME = "X-Agent-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
AGENT_SECRET = os.getenv("VIRTUALS_API_KEY", "lojer_secret_123")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != AGENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Secret Key")
    return api_key


TARGET_ASSETS = ["BTC", "ETH"]

@app.get("/status")
def get_status():
    if os.path.exists("open_positions.json"):
        with open("open_positions.json", "r") as f: return json.load(f)
    return {"message": "No active positions."}

@app.post("/run-all-assets")
def trigger_full_scan(api_key: str = Security(verify_api_key)):
    """این روت توسط Cron-job صدا زده می‌شود تا هر ۵ ارز را اسکن کند"""
    summary = {}
    
    for count, asset in enumerate(TARGET_ASSETS):
        # بررسی حافظه: اگر پوزیشن باز روی این ارز داریم، اسکن را برایش رد کن
        if check_position(asset) == "OPEN":
            summary[asset] = "SKIPPED_ALREADY_OPEN"
            continue
            
        ticker = f"{asset}USDT"
        print(f"🔍 System scanning target {count+1}/5: {ticker}")
        
        try:
            # اجرای مدل هوش مصنوعی برای این ارز خاص
            cmd = ["python", "-m", "src.loj.main", "--ticker", ticker, "--type", "CEX"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            summary[asset] = "SCAN_COMPLETED"
        except subprocess.CalledProcessError as e:
            summary[asset] = f"FAILED: {e.stderr}"
            
    return {
        "status": "scan_finished",
        "results": summary
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)