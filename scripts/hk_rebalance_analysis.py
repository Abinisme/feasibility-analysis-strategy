#!/usr/bin/env python3
"""恒生科技→沪深300换仓+抄底腾讯 量化决策分析"""
import os, time, datetime
import pandas as pd, numpy as np
import tushare as ts

OUT='/Users/yntwt/feasibility-analysis-strategy/data'
ts.set_token(os.environ['TUSHARE_TOKEN'])
p=ts.pro_api()

def fetch(api,**kw):
    """带重试的拉取（60s限流间隔）"""
    for attempt in range(3):
        try:
            df=p.query(api,**kw)
            if df is not None and len(df)>0:
                return df
            time.sleep(60)
        except Exception as e:
            s=str(e)
            if '频率' in s:
                time.sleep(62)
            else:
                code = kw.get('ts_code', kw.get('index_code',''))
                print(f'  X {api} {code}: {s[:60]}')
                return None
    return None

print('=== 港A跨市场数据抓取 ===')
results={}

# 1. 腾讯 00700.HK (半年)
print('1/6 腾讯 00700.HK...')
results['tencent']=fetch('hk_daily',ts_code='00700.HK',start_date='20260101',end_date='20260630')
time.sleep(62)

# 2. 恒生科技ETF (恒科指数代理 - 03033.HK CSOP恒科ETF)
print('2/6 恒生科技ETF 03033.HK...')
results['hstech']=fetch('hk_daily',ts_code='03033.HK',start_date='20260101',end_date='20260630')
time.sleep(62)

# 3. 盈富基金 02800.HK (恒生指数代理)
print('3/6 盈富基金 02800.HK...')
results['hsi']=fetch('hk_daily',ts_code='02800.HK',start_date='20260101',end_date='20260630')
time.sleep(62)

# 4. 沪深300
print('4/6 沪深300...')
results['csi300']=fetch('index_daily',index_code='000300.SH',start_date='20260101',end_date='20260630')
time.sleep(62)

# 5. 恒生ETF (159920.SZ) A股场内
print('5/6 恒生ETF 159920...')
results['hsi_etf_a']=fetch('daily',ts_code='159920.SZ',start_date='20260101',end_date='20260630')
time.sleep(62)

# 6. 沪深300ETF (510300.SH)
print('6/6 沪深300ETF 510300...')
results['csi300_etf']=fetch('daily',ts_code='510300.SH',start_date='20260101',end_date='20260630')

# 保存
for k,df in results.items():
    if df is not None and len(df)>0:
        df.to_csv(f'{OUT}/hk_{k}.csv',index=False)
        print(f'  ✅ {k}: {len(df)}行')

print('\n=== 全部完成 ===')
