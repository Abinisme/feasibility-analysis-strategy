#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10/13 vs 10/12 资金流对比（概念/行业/个股）"""
import warnings
warnings.filterwarnings('ignore')
import pandas as pd

BASE = '/Users/yntwt/feasibility-analysis-strategy'
KW = ['CPO', '封装光学', '光模块', 'PCB', '覆铜', '存储', '封装', '半导体', '芯片',
      '光刻', '集成电路', '算力', '液冷', '服务器', '铜缆', 'HBM', '先进封装', '光通信']

c12 = pd.read_csv(f'{BASE}/data/20261012/fundflow_concept_ths.csv')
c13 = pd.read_csv(f'{BASE}/data/20261013/fundflow_concept_ths.csv')
i12 = pd.read_csv(f'{BASE}/data/20261012/fundflow_industry_ths.csv')
i13 = pd.read_csv(f'{BASE}/data/20261013/fundflow_industry_ths.csv')
s12 = pd.read_csv(f'{BASE}/data/20261012/fundflow_individual_ths.csv', dtype={'股票代码': str})
s13 = pd.read_csv(f'{BASE}/data/20261013/fundflow_individual_ths.csv', dtype={'股票代码': str})

print('=== 科技概念资金流对比（净额亿元）===')
m = c12[['行业', '净额', '行业-涨跌幅']].merge(
    c13[['行业', '净额', '行业-涨跌幅']], on='行业', suffixes=('_12', '_13'))
m = m[m['行业'].str.contains('|'.join(KW), na=False)]
m['净额变化'] = (m['净额_13'] - m['净额_12']).round(2)
print(m.sort_values('净额_13', ascending=False).to_string(index=False))

print('\n=== 行业资金流 TOP（10/13）===')
top13 = i13.nlargest(10, '净额')[['行业', '净额', '行业-涨跌幅']]
top12 = i12.nlargest(10, '净额')[['行业', '净额', '行业-涨跌幅']].rename(
    columns={'净额': '净额_12', '行业-涨跌幅': '涨幅_12'})
print('10/13 前10:'); print(top13.to_string(index=False))
print('10/12 前10:'); print(top12.to_string(index=False))

print('\n=== 8只标的 10/13 个股资金流 ===')
TG = ['688981', '688825', '002371', '300059', '300750', '002463']
for c in TG:
    r13 = s13[s13['股票代码'] == c]
    r12 = s12[s12['股票代码'] == c]
    if len(r13):
        a = r13.iloc[0]
        b = r12.iloc[0] if len(r12) else None
        print(f"  {a['股票简称']:8s} 10/13净额 {str(a['净额']):>10s} (涨{a['涨跌幅']})  |  "
              f"10/12净额 {str(b['净额']) if b is not None else '-':>10s}"
              f" (涨{b['涨跌幅'] if b is not None else '-'})")

print('\n=== 两市个股主力净流入 TOP15（10/13）===')
s13['净额亿'] = pd.to_numeric(s13['净额'].astype(str).str.replace('亿', '', regex=False), errors='coerce')
print(s13.nlargest(15, '净额亿')[['股票简称', '最新价', '涨跌幅', '净额亿', '成交额']].to_string(index=False))
