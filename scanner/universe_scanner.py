import asyncio, ccxt.async_support as ccxt
import pandas as pd, numpy as np
from collections import defaultdict

WINDOW = 20

def tanh_clip(x): return np.tanh(x)

async def fetch_last(exchange, symbol, timeframe, limit=WINDOW):
 o = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
 return pd.DataFrame(o, columns=[‘ts’,‘o’,‘h’,‘l’,‘c’,‘v’])

def quick_score(df):
 if df is None or len(df)<5: return -1e9
 vdelta = (df[‘v’].iloc[-1]/(df[‘v’].iloc[-2]+1e-12))-1
 vrr = df[‘v’].iloc[-1]/(df[‘v’].rolling(3).mean().iloc[-1]+1e-12)
 ema9 = df[‘c’].ewm(span=9,adjust=False).mean().iloc[-1]
 mom = (df[‘c’].iloc[-1]/(ema9+1e-12))-1
 return 0.5tanh_clip(vrr-1)+0.3tanh_clip(vdelta)+0.2*max(0,mom)

class FocusManager:
 def init(self, top_k, buffer, enter_need=2, drop_need=2):
  self.top_k, self.buffer = top_k, buffer
  self.enter_need, self.drop_need = enter_need, drop_need
  self.count_in = defaultdict(int); self.count_out = defaultdict(int); self.focus = set()

 def update(self, ranked):
  top = [s for s,_ in ranked[:self.top_k]]
  buf = set([s for s,_ in ranked[:self.top_k+self.buffer]])
  new_focus = set(self.focus)
  for s,_ in ranked[:self.top_k+self.buffer]:
   if s in self.focus: continue
   if s in top: self.count_in[s]+=1;
    if self.count_in[s]>=self.enter_need: new_focus.add(s)
   else: self.count_in[s]=0
  for s in list(self.focus):
   if s not in buf: self.count_out[s]+=1;
    if self.count_out[s]>=self.drop_need: new_focus.discard(s); self.count_out[s]=0
   else: self.count_out[s]=0
  if len(new_focus)>self.top_k:
   order=[s for s,_ in ranked]; new_focus=set([s for s in order if s in new_focus][:self.top_k])
  self.focus = new_focus; return list(self.focus)

async def scan_loop(cfg):
 ex = getattr(ccxt, cfg[‘exchange’])({‘enableRateLimit’:True})
 tf = cfg[‘timeframe’]; syms = cfg[‘universe’]
 fm = FocusManager(cfg[‘focus_top_k’], cfg[‘focus_buffer’], cfg[‘consec_scans_to_enter’], cfg[‘consec_scans_to_drop’])
 try:
  while True:
   results = {}; batch=20
   for i in range(0,len(syms),batch):
    group=syms[i:i+batch]
    dfs = await asyncio.gather(*[fetch_last(ex,s,tf) for s in group],return_exceptions=True)
    for s,df in zip(group,dfs):
     if isinstance(df,Exception): continue
     results[s]=df
    await asyncio.sleep(0.8)
   scores = {s:quick_score(df) for s,df in results.items()}
   ranked = sorted(scores.items(),key=lambda kv:kv[1],reverse=True)
   focus = fm.update(ranked); print(“Focus:”,sorted(focus))
   await asyncio.sleep(cfg[‘scan_interval_sec’])
 finally: await ex.close()

if name == “main”:
 import yaml, asyncio
 cfg = yaml.safe_load(open(“config.yml”))
 asyncio.run(scan_loop(cfg))
