#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基于70日历史序列：连板/最高板/63日新高新低/昨涨停今表现/涨停家数序列"""
import warnings, json
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

BASE = '/Users/yntwt/feasibility-analysis-strategy'
hist = pd.read_csv(f'{BASE}/data/_cache/history_70d_20261013.csv.gz', dtype={'trade_date': str})
hist = hist.sort_values(['ts_code', 'trade_date']).reset_index(drop=True)
dates = sorted(hist['trade_date'].unique())
LAST, PREV = dates[-1], dates[-2]
print(f'序列 {len(dates)} 天 {dates[0]}~{LAST} | {len(hist)} 行')


def limit_pct(ts_code):
    c = ts_code.split('.')[0]
    if ts_code.endswith('.BJ'):
        return 0.30
    if c.startswith(('300', '301', '688')):
        return 0.20
    return 0.10


hist['lim'] = hist['ts_code'].map(limit_pct)
hist['lim_price'] = (hist['pre_close'] * (1 + hist['lim'])).round(2)
hist['is_lu'] = (hist['close'] - hist['lim_price']).abs() < 0.005
hist['is_ld'] = (hist['close'] - (hist['pre_close'] * (1 - hist['lim'])).round(2)).abs() < 0.005

RES = {}
# ---- 每日涨停/跌停家数（近20日）----
g = hist.groupby('trade_date').agg(lu=('is_lu', 'sum'), ld=('is_ld', 'sum'))
RES['lu_ld_series'] = g.tail(15).reset_index().to_dict('records')
print('\n=== 近15日 涨停/跌停家数 ===')
print(g.tail(15).T.to_string())

# ---- 连板计算（10/13）----
sub = hist[hist['trade_date'] <= LAST].copy()
sub['rk'] = sub.groupby('ts_code')['trade_date'].rank(ascending=False)
recent = sub[sub['rk'] <= 15].sort_values(['ts_code', 'trade_date'], ascending=[True, False])


def streak(grp):
    n = 0
    for v in grp['is_lu']:
        if v:
            n += 1
        else:
            break
    return n


st = recent.groupby('ts_code').apply(streak, include_groups=False)

last_rows = hist[hist['trade_date'] == LAST].set_index('ts_code')
st = st.reindex(last_rows.index).fillna(0).astype(int)
RES['lianban_dist'] = {int(k): int(v) for k, v in st.value_counts().sort_index(ascending=False).items() if k >= 2}
RES['max_board'] = int(st.max())
RES['lianban_count'] = int((st >= 2).sum())
names = pd.read_csv(f'{BASE}/data/20261013/stocks_qq.csv', dtype={'ts_code': str})[['ts_code', 'name', 'amount_yi']]
nm = names.set_index('ts_code').rename(columns={'amount_yi': 'qq_amt'})
top_boards = last_rows.join(st.rename('连板')).join(nm[['name', 'qq_amt']])
tb = top_boards[top_boards['连板'] >= 2].sort_values(['连板', 'qq_amt'], ascending=[False, False])
RES['lianban_top'] = tb.head(25).reset_index()[['ts_code', 'name', '连板', 'close', 'pct_chg', 'qq_amt']].to_dict('records')
print(f'\n=== 连板分布（10/13）=== 连板家数 {RES["lianban_count"]} | 最高板 {RES["max_board"]} 板')
print(tb.head(22)[['name', '连板', 'close', 'pct_chg', 'qq_amt']].to_string())

# ---- 63日新高/新低 ----
past = hist[hist['trade_date'] < LAST]
last63 = sorted(past['trade_date'].unique())[-63:]
p63 = past[past['trade_date'].isin(last63)]
agg = p63.groupby('ts_code').agg(hi=('high', 'max'), lo=('low', 'min'))
j = last_rows[['close']].join(agg)
RES['high63'] = int((j['close'] >= j['hi']).sum())
RES['low63'] = int((j['close'] <= j['lo']).sum())
print(f"\n=== 63日新高/新低 === 新高 {RES['high63']} | 新低 {RES['low63']}")

# ---- 昨涨停今表现 ----
prev_lu = set(hist[(hist['trade_date'] == PREV) & hist['is_lu']]['ts_code'])
today = hist[hist['trade_date'] == LAST].set_index('ts_code')
pv = today.loc[today.index.intersection(list(prev_lu))]
RES['prev_lu_n'] = len(prev_lu)
RES['prev_lu_today_avg'] = round(float(pv['pct_chg'].mean()), 2) if len(pv) else None
RES['prev_lu_today_median'] = round(float(pv['pct_chg'].median()), 2) if len(pv) else None
RES['prev_lu_today_up_ratio'] = round(float((pv['pct_chg'] > 0).mean() * 100), 1) if len(pv) else None
print(f"=== 昨涨停今表现 === {RES['prev_lu_n']}只 | 均值 {RES['prev_lu_today_avg']}% | 中位 {RES['prev_lu_today_median']}% | 翻红 {RES['prev_lu_today_up_ratio']}%")

# ---- 8只标的近期走势 ----
TG = {'688981.SH': '中芯国际', '688825.SH': '长鑫科技', '002371.SZ': '北方华创',
      '300059.SZ': '东方财富', '300750.SZ': '宁德时代', '002463.SZ': '沪电股份'}
print('\n=== 8只标的近6日收盘/涨跌 ===')
for c, n in TG.items():
    s = hist[hist['ts_code'] == c].sort_values('trade_date').tail(6)
    print(f"  {n:6s} " + ' | '.join(f"{r['trade_date'][4:]}:{r['close']}({r['pct_chg']:+.1f}%)" for _, r in s.iterrows()))

with open(f'{BASE}/data/20261013/history_stats.json', 'w', encoding='utf-8') as f:
    json.dump(RES, f, ensure_ascii=False, indent=2, default=str)
print('\n[DONE] history_stats.json')
