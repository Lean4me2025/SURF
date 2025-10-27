import time, datetime as dt, yaml
import pandas as pd, numpy as np
import ccxt
from indicators.volume_stack import add_indicators
from signals.rules import enter_ok, exit_ok, transfer_candidate

def ts_now(): return dt.datetime.utcnow().strftime(”%Y-%m-%d %H:%M:%S”)
def cost_mult(bps): return 1.0 + bps/10000.0

def load_ohlcv(exchange, symbol, timeframe, limit=200):
 o = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
 df = pd.DataFrame(o, columns=[‘ts’,‘open’,‘high’,‘low’,‘close’,‘volume’])
 df[‘ts’] = pd.to_datetime(df[‘ts’], unit=‘ms’); return df

def main():
 cfg = yaml.safe_load(open(‘config.yml’))
 ex = getattr(ccxt, cfg[‘exchange’])({“enableRateLimit”:True})
 timeframe = cfg[‘timeframe’]; symbols = cfg[‘symbols’]; poll_s = cfg[‘poll_seconds’]
 enter_th = cfg[‘enter’]; exit_th = cfg[‘exit’]; xfer_th = cfg[‘transfer’]
 equity = cfg[‘start_equity’]; day_start = equity
 fee_bps = cfg[‘fee_bps’]; slip_bps = cfg[‘slip_bps’]; cap_frac = cfg[‘cap_fraction’]
 loss_cap = cfg[‘daily_loss_cap_pct’]; hard_stop = cfg[‘hard_stop_pct’]; gain_haircut = cfg[‘cost_haircut_on_gains_pct’]
 log_csv = cfg.get(‘log_csv’,True)

 open_pos = None; logs = []
 print(f”[{ts_now()}] SURF live (paper) started. Equity=${equity:.2f}”)

 try:
  while True:
   if (equity - day_start)/day_start <= -loss_cap:
    print(f”[{ts_now()}] Daily loss cap hit. Standing down.”)
    time.sleep(poll_s); continue

   rows = {}
   for s in symbols:
    df = load_ohlcv(ex,s,timeframe,limit=200); df = add_indicators(df)
    rows[s] = df.iloc[-1]

   if open_pos is None:
    cands = [s for s,r in rows.items() if enter_ok(r,enter_th)]
    if cands:
     sym = max(cands,key=lambda s: rows[s][‘vrr’])
     px = rows[sym][‘close’]; size_val = equitycap_frac; size = size_val/px
     cost = sizepx*cost_mult(fee_bps+slip_bps); equity -= cost
     open_pos = {‘sym’:sym,‘entry_px’:px,‘size’:size,‘entry_ts’:rows[sym].name}
     print(f”[{ts_now()}] ENTER {sym} @ {px:.6f} equity={equity:.2f}”)
   else:
    s = open_pos[‘sym’]; r = rows.get(s)
    if r is not None:
     mkt = r[‘close’]
     if (mkt - open_pos[‘entry_px’])/open_pos[‘entry_px’] <= -hard_stop:
      proceeds = open_pos[‘size’]*mkt / cost_mult(fee_bps); equity += proceeds
      print(f”[{ts_now()}] STOP {s} @ {mkt:.6f} eq={equity:.2f}”)
      open_pos = None
     elif exit_ok(r,exit_th):
      px = r[‘close’]; proceeds = open_pos[‘size’]px / cost_mult(fee_bps)
      equity += proceeds; gross = proceeds; pnl_after = gross(1-gain_haircut); equity -= (gross-pnl_after)
      print(f”[{ts_now()}] EXIT {s} @ {px:.6f} eq={equity:.2f}”)
      open_pos = None

      targets = [t for t,rt in rows.items() if t!=s and transfer_candidate(rt,xfer_th)]
      if targets:
       t = max(targets,key=lambda t: rows[t][‘vrr’])
       px = rows[t][‘close’]; size_val = equitycap_frac; size = size_val/px
       cost = sizepx*cost_mult(fee_bps+slip_bps); equity -= cost
       open_pos = {‘sym’:t,‘entry_px’:px,‘size’:size,‘entry_ts’:rows[t].name}
       print(f”[{ts_now()}] TRANSFER → {t} @ {px:.6f} eq={equity:.2f}”)

   if log_csv:
    pd.DataFrame(logs,columns=[“ts”,“sym”,“eq”]).to_csv(“live_log.csv”,index=False)
   time.sleep(poll_s)
 finally: ex.close()

if name == “main”: main()
