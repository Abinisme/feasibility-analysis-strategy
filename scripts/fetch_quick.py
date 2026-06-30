#!/usr/bin/env python3
"""半导体数据抓取 - 快速补全版"""
import os, time
import pandas as pd
import tushare as ts

OUT = '/Users/yntwt/feasibility-analysis-strategy/data'
TOKEN = os.environ.get('TUSHARE_TOKEN')
ts.set_token(TOKEN)
pro = ts.pro_api()

STOCKS = {
    '688981.SH': '中芯国际', '688347.SH': '华虹半导体',
    '002371.SZ': '北方华创', '688012.SH': '中微公司', '688072.SH': '拓荆科技',
    '688200.SH': '华峰测控', '688082.SH': '盛美上海',
    '688126.SH': '沪硅产业', '688019.SH': '安集科技',
    '300655.SH': '晶瑞股份', '002409.SZ': '雅克科技', '300398.SH': '飞凯材料',
    '688720.SH': '艾森股份', '300666.SZ': '江丰电子', '002312.SZ': '鼎龙股份',
    '603998.SH': '方邦股份',
    '601133.SH': '柏诚股份', '603859.SH': '能科科技',
}
ETFs = {'159516.SZ':'半导体设备ETF','159995.SZ':'芯片ETF','512480.SH':'半导体ETF','588000.SH':'科创50ETF','159840.SZ':'半导体材料ETF'}
INDICES = {'000300.SH':'沪深300','399006.SZ':'创业板指','000688.SH':'科创50'}

S, E = '20260506', '20260629'

def save(df, name):
    df.to_csv(f'{OUT}/{name}.csv', index=False, encoding='utf-8-sig')
    print(f'  ✅ {name}: {len(df)}行')

# 1. ETF + 指数行情
print('=== 1. ETF/指数 日K ===')
all_etf = []
for code, name in {**ETFs, **INDICES}.items():
    try:
        df = pro.daily(ts_code=code, start_date=S, end_date=E)
        if df is not None and len(df)>0:
            df['name']=name; df['code']=code
            all_etf.append(df)
            print(f'  {code} {name}: {len(df)}行')
        time.sleep(0.4)
    except Exception as e: print(f'  ❌{code}:{e}'); time.sleep(1)

etf_df = pd.concat(all_etf, ignore_index=True)
old = pd.read_csv(f'{OUT}/batch1_quotes.csv')
old['trade_date']=old['trade_date'].astype(str)
combined = pd.concat([old, etf_df], ignore_index=True).drop_duplicates(subset=['ts_code','trade_date'])
save(combined, 'batch1_quotes')

# 2. 财务指标
print('=== 2. 财务指标(fina_indicator) ===')
all_fin=[]
for i,(code,name) in enumerate(STOCKS.items()):
    try:
        df=pro.fina_indicator(ts_code=code, start_date='20240101', end_date=E,
            fields='ts_code,end_date,ann_date,eps,roe,roe_yearly,grossprofit_margin,netprofit_margin,q_profit_yoy,q_sales_yoy,q_op_yoy,debt_to_assets,op_of_gr,goodsell_of_gr')
        if df is not None and len(df)>0:
            df['name']=name; df['code']=code; all_fin.append(df)
            if (i+1)%5==0: print(f'  进度 {i+1}/{len(STOCKS)} {code} {name}:{len(df)}行')
        time.sleep(1.5)
    except Exception as e: print(f'  ❌{code}:{e}'); time.sleep(2)
save(pd.concat(all_fin,ignore_index=True), 'batch3_financials')

print('=== 2b. 营收净利 ===')
all_inc=[]
for i,(code,name) in enumerate(STOCKS.items()):
    try:
        df=pro.income(ts_code=code, start_date='20240101', end_date=E,
            fields='ts_code,end_date,ann_date,total_revenue,n_income,n_income_attr_p,operate_profit')
        if df is not None and len(df)>0:
            df['name']=name; df['code']=code; all_inc.append(df)
            if (i+1)%5==0: print(f'  进度 {i+1}/{len(STOCKS)} {code} {name}:{len(df)}行')
        time.sleep(1.5)
    except Exception as e: print(f'  ❌{code}:{e}'); time.sleep(2)
save(pd.concat(all_inc,ignore_index=True), 'batch3_income')

# 3. 板块景气度
print('=== 3. 板块景气度 ===')
for sw_code, sw_name in [('801081.SI','半导体'),('801082.SI','元件'),('801085.SI','电子化学品')]:
    try:
        df=pro.sw_daily(ts_code=sw_code, start_date=S, end_date=E)
        if df is not None and len(df)>0:
            df['name']=sw_name; save(df, f'batch5_sw_{sw_name}')
            print(f'  ✅ 申万{sw_name}:{len(df)}行')
        time.sleep(2)
    except Exception as e: print(f'  ❌{sw_name}:{e}')

print('=== 完成！===')
