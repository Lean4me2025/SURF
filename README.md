# SURF
SURF INVESTMENT PROGRAM 102625
FILE: README.md — Project Overview and Quick Start
────────────────────────────────────────────────────────────
SURF – Program Build-Up & Ripple Whale Capture Strategy
Two-tier architecture:
1️⃣ Universe Scanner (~250 coins) → ranks by fresh volume energy.
2️⃣ Focus Engine (8–20 coins) → full rules (ENTER/EXIT/TRANSFER) + risk caps.
Core Signals
Enter → VΔ ≥ +200 %, VRR ≥ 1.5, RSI ≤ 65, MACD-hist rising 2 bars
Exit → VT ≥ 0.20 OR (RSI ≥ 70 AND MACD-hist falling 2 bars)
Transfer → next coin shows VRR ≥ 1.3 OR VΔ ≥ +50 % within 3–9 min
Quick Start
pip install ccxt pandas numpy pyyaml xgboost joblib
python -m sim.backtest
python -m live.surf_signal_bot
python -m scanner.universe_scanner
────────────────────────────────────────────────────────────
END FILE
