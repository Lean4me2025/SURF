import pandas as pd

def enter_ok(row, th):
 return (
  (row.get(‘v_delta’, 0) >= th[‘vdelta_min’]) and
  (row.get(‘vrr’, 0) >= th[‘vrr_min’]) and
  (row.get(‘rsi’, 100) <= th[‘rsi_max’]) and
  (bool(row.get(‘hist_up2’, False)) if th.get(‘macd_hist_up2’, True) else True)
 )

def exit_ok(row, th):
 vt = row.get(‘vt’, None)
 cond_vt = (vt is not None) and (pd.notna(vt)) and (vt >= th[‘vt_min’])
 cond_rsi_macd = (row.get(‘rsi’, 0) >= th[‘rsi_min’]) and (
  bool(row.get(‘hist_dn2’, False)) if th.get(‘macd_hist_dn2’, True) else True)
 return cond_vt or cond_rsi_macd

def transfer_candidate(row, th):
 return (row.get(‘vrr’, 0) >= th[‘vrr_min’]) or (row.get(‘v_delta’, 0) >= th[‘vdelta_min’])
