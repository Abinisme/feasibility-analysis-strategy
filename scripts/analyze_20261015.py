#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-10-14 科技板块 + 8只标的 全栈技术指标量化
- 标的日K：腾讯 ifzq（320根，含10/14）
- 板块指数：同花顺概念指数（截至10/13）+ 10/14实时涨跌幅拼接
输出：data/20261015/tech_quant.json
"""
import json, warnings, urllib.request
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

BASE = '/Users/yntwt/feasibility-analysis-strategy'
OUT = f'{BASE}/data/20261015'

TARGETS = {
    '中芯国际': 'sh688981', '长鑫科技': 'sh688825', '北方华创': 'sz002371',
    '东方财富': 'sz300059', '宁德时代': 'sz300750', '沪电股份': 'sz002463',
    '通讯ETF': 'sh515050', '恒生科技ETF': 'hk03032',
}
# 板块: (同花顺概念名, 10/14实时涨跌幅%)
SECTORS = {
    '光通讯(CPO)': ('共封装光学(CPO)', -3.58),
    'PCB': ('PCB概念', -2.92),
    '存储': ('存储芯片', -3.59),
    '封测': ('先进封装', -3.43),
    '半导体设备材料': ('光刻机', -3.09),
    '芯片设计': ('芯片概念', -3.62),
    '液冷/算力': ('液冷服务器', -3.73),
}


def qq_kline(code):
    url = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,320,qfq'
    d = json.loads(urllib.request.urlopen(url, timeout=20).read().decode('utf-8'))
    node = d['data'][code]
    k = node.get('qfqday') or node.get('day')
    return pd.DataFrame([{'date': r[0], 'open': float(r[1]), 'close': float(r[2]),
                          'high': float(r[3]), 'low': float(r[4]), 'vol': float(r[5])} for r in k])


def ths_index(name):
    import akshare as ak
    df = ak.stock_board_concept_index_ths(symbol=name, start_date='20260101', end_date='20261015')
    df = df.rename(columns={'日期': 'date', '开盘价': 'open', '最高价': 'high',
                            '最低价': 'low', '收盘价': 'close', '成交量': 'vol'})
    df['date'] = df['date'].astype(str)
    return df[['date', 'open', 'high', 'low', 'close', 'vol']]


def metrics(df, label, today_pct=None):
    df = df.copy().reset_index(drop=True)
    if today_pct is not None and df.iloc[-1]['date'][:10] != '2026-10-14':
        pc = float(df.iloc[-1]['close'])
        tc = round(pc * (1 + today_pct / 100), 3)
        df = pd.concat([df, pd.DataFrame([{'date': '2026-10-15(拼接)', 'open': np.nan,
                                           'high': np.nan, 'low': np.nan, 'close': tc, 'vol': np.nan}])],
                       ignore_index=True)
    c = df['close'].astype(float); h = df['high'].astype(float); l = df['low'].astype(float)
    px = float(c.iloc[-1])
    ma = {f'MA{n}': round(float(c.rolling(n).mean().iloc[-1]), 3) for n in (5, 10, 20, 60)}
    delta = c.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / 5, adjust=False).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / 5, adjust=False).mean()
    rsi5 = round(float(100 - 100 / (1 + up.iloc[-1] / dn.iloc[-1])), 1) if dn.iloc[-1] > 0 else 100.0
    e12 = c.ewm(span=12, adjust=False).mean(); e26 = c.ewm(span=26, adjust=False).mean()
    dif = e12 - e26; dea = dif.ewm(span=9, adjust=False).mean(); hist = (dif - dea) * 2

    def pct(n):
        return round((px / float(c.iloc[-1 - n]) - 1) * 100, 2) if len(c) > n else None
    hh20, ll20 = float(h.tail(20).max()), float(l.tail(20).min())
    hh60 = float(h.tail(60).max())
    sup = max(ll20, ma['MA20'] if ma['MA20'] < px else ll20)
    res = hh20 if hh20 > px else hh60
    return {'label': label, 'date': df.iloc[-1]['date'], 'close': px,
            'pct_chg_today': round((px / float(c.iloc[-2]) - 1) * 100, 2),
            **ma, 'RSI5': rsi5, 'MACD_DIF': round(float(dif.iloc[-1]), 3),
            'MACD_DEA': round(float(dea.iloc[-1]), 3), 'MACD_hist': round(float(hist.iloc[-1]), 3),
            'MACD_hist_prev': round(float(hist.iloc[-2]), 3),
            'MA5_dev': round((px / ma['MA5'] - 1) * 100, 2),
            'MA20_dev': round((px / ma['MA20'] - 1) * 100, 2),
            'MA60_dev': round((px / ma['MA60'] - 1) * 100, 2) if ma['MA60'] == ma['MA60'] else None,
            'pct_3d': pct(3), 'pct_5d': pct(5), 'pct_10d': pct(10), 'pct_20d': pct(20),
            'high20': hh20, 'low20': ll20, 'high60': hh60,
            'support': round(sup, 3), 'resistance': round(res, 3),
            'up_space_pct': round((res - px) / px * 100, 2),
            'down_risk_pct': round((px - sup) / px * 100, 2),
            'RR': round((res - px) / (px - sup), 2) if px > sup else None,
            'vol_ratio': round(float(df['vol'].iloc[-1] / df['vol'].tail(6).head(5).mean()), 2)
            if pd.notna(df['vol'].iloc[-1]) else None}


RES = {'targets': {}, 'sectors': {}}
print('=== 8 只标的（10/14）===')
for name, code in TARGETS.items():
    try:
        m = metrics(qq_kline(code), name)
        RES['targets'][name] = m
        print(f"  {name:8s} 收{m['close']:>9.3f} {m['pct_chg_today']:>+6.2f}% | MA5 {m['MA5']:>8.3f} MA20 {m['MA20']:>8.3f} "
              f"MA60 {m['MA60']:>8.3f} | RSI5 {m['RSI5']:>5.1f} | MACD柱 {m['MACD_hist']:>+7.3f} | "
              f"支撑{m['support']:>8.3f} 压力{m['resistance']:>8.3f} RR {m['RR']}")
    except Exception as e:
        print(f'  [ERR] {name}: {str(e)[:90]}')

print('\n=== 科技板块 ===')
for name, (ths, pct) in SECTORS.items():
    try:
        df = ths_index(ths)
        m = metrics(df, name, today_pct=pct)
        RES['sectors'][name] = m
        print(f"  {name:14s} 今{pct:>+5.2f}% 收{m['close']:>9.2f} | MA5偏离 {m['MA5_dev']:>+6.2f}% MA20偏离 {m['MA20_dev']:>+7.2f}% "
              f"MA60偏离 {str(m['MA60_dev']):>+7s}% | RSI5 {m['RSI5']:>5.1f} | 5日 {str(m['pct_5d']):>6s}% 20日 {str(m['pct_20d']):>6s}% | "
              f"距60高 {round((m['resistance']/m['close']-1)*100,2):>+6.2f}%")
    except Exception as e:
        print(f'  [ERR] {name}: {str(e)[:90]}')

with open(f'{OUT}/tech_quant.json', 'w', encoding='utf-8') as f:
    json.dump(RES, f, ensure_ascii=False, indent=2, default=str)
print(f'\n[DONE] {OUT}/tech_quant.json')
