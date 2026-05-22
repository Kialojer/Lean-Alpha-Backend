from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
import json
import os
import subprocess
from pydantic import BaseModel

app = FastAPI(title="Lean Alpha Trader - Virtuals Protocol Gateway")

# ایجاد یک لایه امنیتی ساده برای اینکه هر کسی نتواند به API شما درخواست بفرستد
API_KEY_NAME = "X-Agent-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
AGENT_SECRET = os.getenv("VIRTUALS_API_KEY", "lojer_secret_123")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != AGENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Agent Secret Key")
    return api_key

class TradeRequest(BaseModel):
    ticker: str = "BTC"
    market_type: str = "CEX"

@app.get("/status")
def get_status():
    """position"""
    if os.path.exists("open_positions.json"):
        with open("open_positions.json", "r") as f:
            return json.load(f)
    return {"message": "No active positions in memory."}

@app.post("/run-analysis")
def trigger_agent_pipeline(request: TradeRequest, api_key: str = Security(verify_api_key)):
    """virtual pro call thsi agent"""
    try:
        # اجرای main.py به صورت یک پروسه مجزا با آرگومان‌های ارسالی
        cmd = ["python", "-m", "src.loj.main", "--ticker", request.ticker, "--type", request.market_type]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # خواندن آخرین سیگنال ساخته شده
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)