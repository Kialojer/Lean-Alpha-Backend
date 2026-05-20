# 🚀 Lean Alpha Trading Engine

> An autonomous AI trading system that thinks like a quant, posts like a degen.

Built with **CrewAI** + **Python** — analyzes CEX & DEX markets in real-time using technical indicators, macro data, sentiment signals, and off-chain derivatives data to generate high-conviction trade setups and viral Crypto Twitter posts.

---

## ⚡ What It Does

```
Market Data (CEX/DEX)
        ↓
  📊 Quant Judge Agent          ← scores conviction 0–100, defines R:R levels
        ↓
  ✍️  Alpha Narrator Agent      ← writes a viral X post with exact trade params
        ↓
  🐦 Output: Trade Setup + Tweet
```

---

## 🧠 Core Features

| Feature | Details |
|---|---|
| **CEX Support** | Binance — real-time OHLCV, RSI, MACD, Volume |
| **DEX Support** | DexScreener — on-chain price, liquidity, volume |
| **Derivatives** | Binance Futures — Funding Rate & Open Interest analysis |
| **Macro Signals** | DXY trend, Fear & Greed Index, sentiment score |
| **Dual-Agent System** | Quant Judge → Alpha Narrator pipeline (CrewAI) |
| **Dynamic R:R** | Score-based risk management (1:2 / 1:2.5 / 1:3) |
| **Viral Output** | Auto-generated X post with entry, TP, SL + alpha rationale |

---

## 🏗️ Architecture

```
lean_alpha/
├── agents/
│   ├── judge_agent.py        # Quant analyst — scores the setup
│   └── narrator_agent.py     # Crypto Twitter alpha caller
├── tasks/
│   ├── judge_task.py         # Market analysis + price level calculation
│   └── narrate_task.py       # X post generation
├── tools/
│   ├── cex_fetcher.py        # Binance REST API
│   ├── dex_fetcher.py        # DexScreener API
│   └── derivatives.py        # Funding rate + OI fetcher
├── crew.py                   # CrewAI pipeline orchestration
├── main.py                   # Entry point
└── config.yaml               # Symbols, thresholds, R:R settings
```

---

## 📊 Scoring & Risk Logic

```
Score ≥ 75   →  Bullish  🟢  LONG   |  R:R = 1:3
Score 50–74  →  Neutral  🟡  WAIT   |  R:R = 1:2.5
Score 30–49  →  Bearish  🟠  SHORT  |  R:R = 1:2
Score < 30   →  HighRisk 🔴  AVOID  |  No trade
```

**Risk Distance** is calculated dynamically from nearest support/resistance — never hardcoded. Always validated: `SL < Entry < TP` for LONG, `TP < Entry < SL` for SHORT.

---

## 🚀 Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/lean-alpha-engine.git
cd lean-alpha-engine
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your_key_here   # or OPENAI_API_KEY
BINANCE_API_KEY=your_key_here
BINANCE_SECRET=your_secret_here
```

### 3. Run

```bash
python main.py --symbol BTC --market cex
python main.py --symbol PEPE --market dex
```

---

## 📤 Sample Output

```
=====================================================
🚀 FINAL OUTPUT FOR X
=====================================================

$BTC just got its stops hunted below 91K — smart money's been waiting for this 👀

🎯 SHORT | Entry: 91,240 | TP: 89,150 | SL: 92,480

🧠 The Alpha: RSI cooling at 43 with -18% volume divergence, funding rate flipped
negative (-0.021%) and OI dropped 340M — classic smart money exit trap.

Bears don't need conviction, they just need patience. $91K was bait. #Crypto #BTC #Derivatives
```

---

## 🛠️ Tech Stack

- **[CrewAI](https://github.com/joaomdmoura/crewAI)** — multi-agent orchestration
- **[Python 3.11+](https://python.org)**
- **Binance REST & Futures API**
- **DexScreener API**
- **Anthropic Claude / OpenAI** (LLM backend, configurable)

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.
Nothing here is financial advice. Trade at your own risk.
The agents are opinionated by design — always DYOR.

---

## 👤 Author

Built by **Kiarash.T.N**

> *"Don't trade the chart. Trade the story behind the chart."*