import pandas as pd
import numpy as np

def add_indicators(df, rsi_len=14, macd=(12,26,9), vrr_len=3, vt_fast=4, vt_slow=8):
 “”“Add VΔ, VRR, VT, RSI and MACD-hist indicators to a DataFrame.”””
 df = df.copy()
 df[‘v_delta’] = df[‘volume’].pct_change().fillna(0.0)
 df[‘vrr’] = df[‘volume’] / df[‘volume’].rolling(vrr_len).mean()
 df[‘vrr’] = df[‘vrr’].replace([np.inf, -np.inf], np.nan).fillna(0.0)
 fast = df[‘volume’].rolling(vt_fast).mean()
 slow = df[‘volume’].rolling(vt_slow).mean()
 df[‘vt’] = (fast - slow) / slow.replace(0, np.nan)
 delta = df[‘close’].diff()
 up = delta.clip(lower=0.0); down = -delta.clip(upper=0.0)
 roll_up = up.rolling(rsi_len).mean()
 roll_down = down.rolling(rsi_len).mean().replace(0, np.nan)
 rs = roll_up / roll_down
 df[‘rsi’] = 100 - (100 / (1 + rs))
 ema_fast = df[‘close’].ewm(span=macd[0], adjust=False).mean()
 ema_slow = df[‘close’].ewm(span=macd[1], adjust=False).mean()
 macd_line = ema_fast - ema_slow
 signal = macd_line.ewm(span=macd[2], adjust=False).mean()
 df[‘macd_hist’] = macd_line - signal
 dh1 = df[‘macd_hist’].diff(); dh2 = df[‘macd_hist’].diff(2)
 df[‘hist_up2’] = (dh1 > 0) & (dh2 > 0)
 df[‘hist_dn2’] = (dh1 < 0) & (dh2 < 0)
 return df
