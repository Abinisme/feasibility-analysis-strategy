#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Tushare 拉取 2026-09-11 指数/个股/ETF 行情"""
import os, time
import tushare as ts

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()

D = '20260911'

IDX = {'000001.SH': '上证指数', '399001.SZ': '深证成指', '399006.SZ': '创业板指',
       '000688.SH': '科创50', '899050.BJ': '北证50'}
STK = {'300308.SZ': '中际旭创', '300502.SZ': '新易盛', '300394.SZ': '天孚通信',
       '002463.SZ': '沪电股份', '688981.SH': '中芯国际', '002371.SZ': '北方华创',
       '300059.SZ': '东方财富', '300750.SZ': '宁德时代', '688825.SH': '长鑫科技'}
ETF = {'515050.SH': '通信ETF'}

print('=== index ===')
for code, name in IDX.items():
    try:
        df = pro.index_daily(ts_code=code, start_date=D, end_date=D)
        if df is not None and len(df):
            r = df.iloc[0]
            print(f'{name} {code}: close={r["close"]} pct={r["pct_chg"]}% amount={r["amount"]}万 open={r["open"]} high={r["high"]} low={r["low"]}')
        else:
            print(f'{name} {code}: NO DATA')
        time.sleep(0.35)
    except Exception as e:
        print(f'{name} {code}: ERR {e}')

print('=== stock ===')
for code, name in STK.items():
    try:
        df = pro.daily(ts_code=code, start_date=D, end_date=D)
        if df is not None and len(df):
            r = df.iloc[0]
            print(f'{name} {code}: close={r["close"]} pct={r["pct_chg"]}% vol={r["vol"]} amount={r["amount"]}千元 open={r["open"]} high={r["high"]} low={r["low"]}')
        else:
            print(f'{name} {code}: NO DATA')
        time.sleep(0.35)
    except Exception as e:
        print(f'{name} {code}: ERR {e}')

print('=== etf ===')
for code, name in ETF.items():
    try:
        df = pro.fund_daily(ts_code=code, start_date=D, end_date=D)
        if df is not None and len(df):
            r = df.iloc[0]
            print(f'{name} {code}: close={r["close"]} pct={r["pct_chg"]}% amount={r["amount"]} open={r["open"]} high={r["high"]} low={r["low"]}')
        else:
            print(f'{name} {code}: NO DATA')
    except Exception as e:
        print(f'{name} {code}: ERR {e}')

print('=== 近5日收盘 (MA5用) ===')
for code, name in {**STK, **{k: v for k, v in IDX.items() if k != '899050.BJ'}}.items():
    try:
        df = pro.daily(ts_code=code, start_date='20260901', end_date=D) if code.endswith(('.SZ', '.SH')) and code not in IDX else pro.index_daily(ts_code=code, start_date='20260901', end_date=D)
        if df is not None and len(df):
            seq = ' '.join(f'{r["trade_date"]}:{r["close"]}' for _, r in df.iterrows())
            print(f'{name}: {seq}')
        time.sleep(0.35)
    except Exception as e:
        print(f'{name}: ERR {e}')
