import pandas as pd
import numpy as np
from indicators.volume_stack import add_indicators
from signals.rules import enter_ok, exit_ok, transfer_candidate

def backtest(df_map, watchlist, fee_bps=10, slip_bps=20, cap_frac=0.25,
     enter_th=None, exit_th=None, xfer_th=None, gain_haircut_pct=0.10):
 “”“Simulate SURF logic over multiple symbols.”””
 enter_th = enter_th or {‘vdelta_min’:2.0,‘vrr_min’:1.5,‘rsi_max’:65,‘macd_hist_up2’:True}
 exit_th  = exit_th  or {‘vt_min’:0.20,‘rsi_min’:70,‘macd_hist_dn2’:True}
 xfer_th  = xfer_th  or {‘vrr_min’:1.3,‘vdelta_min’:0.5}

 for s in watchlist:
  df_map[s] = add_indicators(df_map[s])

 equity = 1000.0; pos = None; trades = []
 ts_all = sorted(set().union(*[set(df_map[s][‘ts’]) for s in watchlist]))

 def _cost_mult(bps): return 1.0 + bps/10000.0

 for ts in ts_all:
  rows = {}
  for s in watchlist:
   r = df_map[s]; rr = r[r[‘ts’]==ts]
   if not rr.empty: rows[s] = rr.iloc[-1]

  if pos is None:
   cands = [s for s,r in rows.items() if enter_ok(r, enter_th)]
   if cands:
    sym = max(cands, key=lambda s: rows[s][‘vrr’])
    px = rows[sym][‘close’]; size_val = equity * cap_frac; size = size_val / px
    cost = sizepx_cost_mult(fee_bps+slip_bps); equity -= cost
    pos = {‘sym’:sym,‘entry_px’:px,‘size’:size,‘entry_ts’:ts}
  else:
   s = pos[‘sym’]; r = rows.get(s)
   if r is not None and exit_ok(r, exit_th):
    px_exit = r[‘close’]; proceeds = pos[‘size’]*px_exit / _cost_mult(fee_bps)
    equity += proceeds
    gross_gain = proceeds
    pnl_after = gross_gain * (1.0 - gain_haircut_pct)
    equity -= (gross_gain - pnl_after)
    trades.append({‘enter_ts’:pos[‘entry_ts’],‘exit_ts’:ts,‘sym’:s,
     ‘entry_px’:pos[‘entry_px’],‘exit_px’:px_exit,‘pnl_after’:pnl_after})
    pos = None

    targets = [t for t,rt in rows.items() if t!=s and transfer_candidate(rt, xfer_th)]
    if targets:
     t = max(targets, key=lambda t: rows[t][‘vrr’])
     px = rows[t][‘close’]; size_val = equity * cap_frac; size = size_val / px
     cost = sizepx_cost_mult(fee_bps+slip_bps); equity -= cost
     pos = {‘sym’:t,‘entry_px’:px,‘size’:size,‘entry_ts’:ts}

 if pos is not None:
  last = df_map[pos[‘sym’]].iloc[-1]; equity += pos[‘size’] * last[‘close’]
  trades.append({‘enter_ts’:pos[‘entry_ts’],‘exit_ts’:last[‘ts’],‘sym’:pos[‘sym’],
    ‘entry_px’:pos[‘entry_px’],‘exit_px’:last[‘close’],‘pnl_after’:pos[‘size’]*last[‘close’]})

 return equity, pd.DataFrame(trades)

if name == “main”:
 print(“Backtest module ready. Wire your CSVs in main to run.”)
