#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补算 2026-10-12 的技术指标与连板统计（数据源：70日历史序列 + 同花顺板块指数）"""
import json, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

BASE = '/Users/yntwt/feasibility-analysis-strategy'
OUT = f'{BASE}/data/20261012'
DATE = '20261012'
hist = pd.read_csv(f'{BASE}/data/_cache/history_70d_20261013.csv.gz', dtype={'trade_date': str})
hist = hist.sort_values(['ts_code', 'trade_date']).reset_index(drop=True)
dates = sorted(hist['trade_date'].unique())
i = dates.index(DATE)
dates = dates[:i + 1]

TG = {'688981.SH': '中芯国际', '688825.SH': '长鑫科技', '002371.SZ': '北方华创',
      '300059.SZ': '东方财富', '300750.SZ': '宁德时代', '002463.SZ': '沪电股份'}
RES = {'targets': {}, 'sectors': {}}


def metrics(df, label):
    df = df.reset_index(drop=True)
    c = df['close'].astype(float); h = df['high'].astype(float); l = df['low'].astype(float)
    px = float(c.iloc[-1])
    ma = {f'MA{n}': round(float(c.rolling(n).mean().iloc[-1]), 3) for n in (5, 10, 20, 60)}
    delta = c.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / 5, adjust=False).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / 5, adjust=False).mean()
    rsi5 = round(float(100 - 100 / (1 + up.iloc[-1] / dn.iloc[-1])), 1) if dn.iloc[-1] > 0 else 100.0
    e12 = c.ewm(span=12, adjust=False).mean(); e26 = c.ewm(span=26, adjust=False).mean()
    dif = e12 - e26; dea = dif.ewm(span=9, adjust=False).mean()
    def pct(n):
        return round((px / float(c.iloc[-1 - n]) - 1) * 100, 2) if len(c) > n else None
    hh20, ll20 = float(h.tail(20).max()), float(l.tail(20).min())
    hh60 = float(h.tail(60).max())
    sup = max(ll20, ma['MA20'] if ma['MA20'] < px else ll20)
    res = hh20 if hh20 > px else hh60
    return {'label': label, 'close': px, 'pct_chg': round(float(df['pct_chg'].iloc[-1]), 2) if 'pct_chg' in df else None,
            **ma, 'RSI5': rsi5, 'MACD_DIF': round(float(dif.iloc[-1]), 3),
            'MACD_DEA': round(float(dea.iloc[-1]), 3), 'MACD_hist': round(float((dif - dea).iloc[-1] * 2), 3),
            'MA5_dev': round((px / ma['MA5'] - 1) * 100, 2), 'MA20_dev': round((px / ma['MA20'] - 1) * 100, 2),
            'MA60_dev': round((px / ma['MA60'] - 1) * 100, 2) if ma['MA60'] == ma['MA60'] else None,
            'pct_5d': pct(5), 'pct_10d': pct(10), 'pct_20d': pct(20),
            'high20': hh20, 'low20': ll20, 'high60': hh60,
            'support': round(sup, 3), 'resistance': round(res, 3),
            'RR': round((res - px) / (px - sup), 2) if px > sup else None}


print('=== 8只标的（10/12收盘口径）===')
for code, name in TG.items():
    sub = hist[(hist['ts_code'] == code) & (hist['trade_date'] <= DATE)]
    if len(sub) < 20:
        print(f'  [SKIP] {name} 数据不足({len(sub)}天)'); continue
    m = metrics(sub, name)
    RES['targets'][name] = m
    print(f"  {name:6s} 收{m['close']:>8.2f}({m['pct_chg']:+.2f}%) MA5 {m['MA5']:>8.2f} MA20 {m['MA20']:>8.2f} "
          f"MA60 {str(m['MA60']):>8s} RSI5 {m['RSI5']:>5.1f} MACD {m['MACD_hist']:>+7.3f} RR {m['RR']}")

# 板块指数（同花顺，截至10/12）
print('\n=== 科技板块（同花顺，10/12）===')
import akshare as ak
SEC = {'光通讯(CPO)': '共封装光学(CPO)', 'PCB': 'PCB概念', '存储': '存储芯片',
       '封测': '先进封装', '半导体设备材料': '光刻机', '芯片设计': '芯片概念', '液冷/算力': '液冷服务器'}
for name, ths in SEC.items():
    try:
        df = ak.stock_board_concept_index_ths(symbol=ths, start_date='20260101', end_date='20261013')
        df = df.rename(columns={'日期': 'date', '最高价': 'high', '最低价': 'low', '收盘价': 'close'})
        df['date'] = df['date'].astype(str)
        m = metrics(df, name)
        RES['sectors'][name] = m
        print(f"  {name:12s} 收{m['close']:>9.2f}({m['pct_chg']:+.2f}%) MA5偏离 {m['MA5_dev']:>6.2f}% MA20偏离 {m['MA20_dev']:>7.2f}% "
              f"RSI5 {m['RSI5']:>5.1f} 5日 {str(m['pct_5d']):>7s} 20日 {str(m['pct_20d']):>7s} 距60高 {round((m['resistance']/m['close']-1)*100,2):>6.2f}%")
    except Exception as e:
        print(f'  [ERR] {name}: {str(e)[:70]}')

# 连板/新高新低（10/12）
print('\n=== 连板与广度（10/12）===')
h = hist[hist['trade_date'] <= DATE]

def limit_pct(ts):
    c = ts.split('.')[0]
    if ts.endswith('.BJ'):
        return 0.30
    if c.startswith(('300', '301', '688')):
        return 0.20
    return 0.10

h = h.copy()
h['lim'] = h['ts_code'].map(limit_pct)
# 用涨跌幅阈值判定（避免 round 银行家舍入导致漏判，如 11.385→11.39 的进位问题）
h['is_lu'] = h['pct_chg'] >= h['lim'] * 100 - 0.12
last = h[h['trade_date'] == DATE].set_index('ts_code')
names = pd.read_csv(f'{BASE}/data/20261012/stocks_qq.csv', dtype={'ts_code': str}).set_index('ts_code')['name']
sub = h[h['trade_date'].isin(sorted(h['trade_date'].unique())[-15:])].sort_values(['ts_code', 'trade_date'], ascending=[True, False])
def streak(g):
    n = 0
    for v in g['is_lu']:
        n = n + 1 if v else n
        if not v:
            break
    return n
st = sub.groupby('ts_code').apply(streak, include_groups=False).reindex(last.index).fillna(0).astype(int)
RES['lianban_count'] = int((st >= 2).sum())
RES['max_board'] = int(st.max())
tb = last.join(st.rename('连板')).join(names.rename('name'))
tbp = tb[tb['连板'] >= 2].sort_values('连板', ascending=False)
RES['lianban_top'] = tbp.head(25).reset_index()[['ts_code', 'name', '连板', 'close', 'pct_chg']].to_dict('records')
print(f"  连板家数 {RES['lianban_count']} | 最高板 {RES['max_board']} 板")
print(tbp.head(15)[['name', '连板', 'close', 'pct_chg']].to_string())
past = h[h['trade_date'] < DATE]
p63 = past[past['trade_date'].isin(sorted(past['trade_date'].unique())[-63:])]
agg = p63.groupby('ts_code').agg(hi=('high', 'max'), lo=('low', 'min'))
j = last[['close']].join(agg)
RES['high63'] = int((j['close'] >= j['hi']).sum()); RES['low63'] = int((j['close'] <= j['lo']).sum())
print(f"  63日新高/新低: {RES['high63']} / {RES['low63']}")

with open(f'{OUT}/tech_quant_1012.json', 'w', encoding='utf-8') as f:
    json.dump(RES, f, ensure_ascii=False, indent=2, default=str)
print(f'\n[DONE] {OUT}/tech_quant_1012.json')
