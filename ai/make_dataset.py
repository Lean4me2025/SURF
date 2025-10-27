import pandas as pd
import numpy as np

def label_wave(df, look_ahead=5, tp=0.03, mdd=0.02):
    """
    Create a binary label per bar:
      1 if within next `look_ahead` bars price reaches +tp (take-profit)
        AND never drops below -mdd (max drawdown) from entry;
      else 0.
    Expects columns: ['close'] already aligned with indicators.
    """
    df = df.copy()
    closes = df['close'].values
    n = len(df)
    fwd_max = np.full(n, np.nan)
    fwd_min = np.full(n, np.nan)

    for i in range(n - look_ahead):
        window = closes[i + 1 : i + 1 + look_ahead]
        if window.size:
            fwd_max[i] = np.max(window)
            fwd_min[i] = np.min(window)

    entry = closes
    peak_ret = (fwd_max - entry) / entry
    worst_dd = (fwd_min - entry) / entry
    df['label'] = ((peak_ret >= tp) & (worst_dd >= -mdd)).astype(int)
    return df


def build_features(df):
    """
    Assemble ML feature set from indicator-enriched DataFrame.
    Requires columns created by indicators/volume_stack.py.
    """
    df = df.copy()
    feats = pd.DataFrame(index=df.index)
    feats['v_delta']   = df['v_delta']
    feats['vrr']       = df['vrr']
    feats['vt']        = df['vt']
    feats['rsi']       = df['rsi']
    feats['macd_hist'] = df['macd_hist']
    feats['ret1']      = df['close'].pct_change(1)
    feats['ret2']      = df['close'].pct_change(2)
    feats['vret1']     = df['volume'].pct_change(1)
    feats = feats.replace([np.inf, -np.inf], np.nan).dropna()
    return feats
