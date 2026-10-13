#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史序列拉取（全市场 daily，用于连板/新高新低/技术指标）
用法: python3 scripts/fetch_history.py [N=70] [end=YYYYMMDD]
输出: data/_cache/history_{N}d_{end}.csv.gz
"""
import os, sys, time, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import tushare as ts

BASE = '/Users/yntwt/feasibility-analysis-strategy'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 70
END = sys.argv[2] if len(sys.argv) > 2 else time.strftime('%Y%m%d')
os.makedirs(f'{BASE}/data/_cache', exist_ok=True)
OUTP = f'{BASE}/data/_cache/history_{N}d_{END}.csv.gz'

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()

cal = pro.trade_cal(exchange='SSE', start_date='20260601', end_date=END, is_open='1')
dates = sorted(cal['cal_date'].tolist())[-N:]
print(f'[{time.strftime("%H:%M:%S")}] 目标 {len(dates)} 个交易日: {dates[0]} ~ {dates[-1]}', flush=True)

frames = []
for i, d in enumerate(dates):
    for attempt in range(3):
        try:
            df = pro.daily(trade_date=d)
            if len(df):
                frames.append(df)
                print(f'[{time.strftime("%H:%M:%S")}] {i+1}/{len(dates)} {d}: {len(df)}行', flush=True)
                break
            else:
                print(f'[{time.strftime("%H:%M:%S")}] {i+1}/{len(dates)} {d}: EMPTY', flush=True)
                break
        except Exception as e:
            print(f'  [RETRY {attempt+1}] {d}: {str(e)[:80]}', flush=True)
            time.sleep(3)
    time.sleep(0.4)

allD = pd.concat(frames, ignore_index=True)
allD['trade_date'] = allD['trade_date'].astype(str)
allD.to_csv(OUTP, index=False, compression='gzip')
print(f'[DONE] {len(allD)} 行 -> {OUTP}', flush=True)
