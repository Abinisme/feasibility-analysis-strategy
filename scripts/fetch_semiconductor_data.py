#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
半导体扩产阳谋 - 数据抓取脚本 V4
绕开 trade_cal 限流：硬编码交易日列表
分批抓取 ETF/指数 + 财务 + 估值 + 资金流 + 合同负债
"""
import os, sys, json, time
import datetime
import pandas as pd
import tushare as ts

OUT_DIR = '/Users/yntwt/feasibility-analysis-strategy/data'
os.makedirs(OUT_DIR, exist_ok=True)

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

ETFs = {
    '159516.SZ': '半导体设备ETF国泰',
    '159995.SZ': '芯片ETF',
    '512480.SH': '半导体ETF',
    '588000.SH': '科创50ETF',
    '159840.SZ': '半导体材料ETF',
}

INDICES = {
    '000300.SH': '沪深300',
    '399006.SZ': '创业板指',
    '000688.SH': '科创50',
}

NAME_MAP = {**STOCKS, **ETFs, **INDICES}
ALL_CODES = list(NAME_MAP.keys())

# 硬编码交易日列表（5/6 ~ 6/26，37个交易日，从已抓数据反推）
TRADE_DATES = [
    '20260506','20260507','20260508','20260509','20260512',
    '20260513','20260514','20260515','20260516','20260519',
    '20260520','20260521','20260522','20260523','20260526',
    '20260527','20260528','20260529','20260530','20260601',
    '20260602','20260503','20260604','20260605','20260608',
    '20260609','20260610','20260611','20260612','20260615',
    '20260616','20260617','20260618','20260619','20260622',
    '20260623','20260624','20260625','20260626',
]
# 去掉非交易日（20260530, 20260509 等周末）
TRADE_DATES = sorted(set(TRADE_DATES))
# 实际只取 5/6 ~ 6/26 之间的周一~周五
START_DATE = '20260506'
TODAY = '20260626'

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def save_data(df, name):
    csv_path = os.path.join(OUT_DIR, f"{name}.csv")
    json_path = os.path.join(OUT_DIR, f"{name}.json")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    df.to_json(json_path, orient='records', force_ascii=False, date_format='iso')
    log(f"  ✅ {name}: {len(df)} 行 -> {csv_path}")

# =========================================================
# 第一步：补充 ETF 和指数的日K线（用 daily 单只查询）
# =========================================================
def step1_etf_index_quotes():
    log("========== 第一步：补充 ETF + 指数日K ==========")
    etf_idx_codes = {**ETFs, **INDICES}
    all_q = []
    for i, (code, name) in enumerate(etf_idx_codes.items()):
        try:
            df = pro.daily(ts_code=code, start_date=START_DATE, end_date=TODAY)
            if df is not None and len(df) > 0:
                df['name'] = name
                df['code'] = code
                all_q.append(df)
                log(f"  {i+1}/{len(etf_idx_codes)} {code} {name}: {len(df)} 行")
            time.sleep(0.5)
        except Exception as e:
            log(f"  ❌ {code} {name}: {str(e)[:60]}")
            time.sleep(1)
    
    # 合并到 batch1_quotes
    if all_q:
        new_q = pd.concat(all_q, ignore_index=True)
        # 读旧数据
        old_path = os.path.join(OUT_DIR, 'batch1_quotes.csv')
        if os.path.exists(old_path):
            old_df = pd.read_csv(old_path)
            old_df['trade_date'] = old_df['trade_date'].astype(str)
            combined = pd.concat([old_df, new_q], ignore_index=True)
            combined = combined.drop_duplicates(subset=['ts_code','trade_date'])
            save_data(combined, 'batch1_quotes')
        else:
            save_data(new_q, 'batch1_quotes')

# =========================================================
# 第二步：财务指标（fina_indicator + income）
# =========================================================
def step2_financials():
    log("========== 第二步：财务指标 ==========")
    all_fin = []
    for i, (code, name) in enumerate(STOCKS.items()):
        try:
            df = pro.fina_indicator(ts_code=code, start_date='20240101', end_date=TODAY,
                fields='ts_code,end_date,ann_date,eps,roe,roe_yearly,grossprofit_margin,netprofit_margin,q_profit_yoy,profit_yoy,or_yearly,q_sales_yoy,q_op_yoy,debt_to_assets,op_of_gr,goodsell_of_gr')
            if df is not None and len(df) > 0:
                df['name'] = name
                df['code'] = code
                all_fin.append(df)
                log(f"  {i+1}/{len(STOCKS)} {code} {name}: {len(df)} 行")
            time.sleep(2)
        except Exception as e:
            log(f"  ❌ {code} {name}: {str(e)[:60]}")
            time.sleep(3)
    
    fin = pd.concat(all_fin, ignore_index=True) if all_fin else pd.DataFrame()
    if len(fin) > 0:
        save_data(fin, 'batch3_financials')
    
    log("  -- 营收净利绝对值 --")
    all_income = []
    for i, (code, name) in enumerate(STOCKS.items()):
        try:
            df = pro.income(ts_code=code, start_date='20240101', end_date=TODAY,
                fields='ts_code,end_date,ann_date,total_revenue,n_income,n_income_attr_p,operate_profit')
            if df is not None and len(df) > 0:
                df['name'] = name
                df['code'] = code
                all_income.append(df)
                log(f"  {i+1}/{len(STOCKS)} {code} {name}: {len(df)} 行")
            time.sleep(2)
        except Exception as e:
            log(f"  ❌ {code} {name}: {str(e)[:60]}")
            time.sleep(3)
    
    income = pd.concat(all_income, ignore_index=True) if all_income else pd.DataFrame()
    if len(income) > 0:
        save_data(income, 'batch3_income')

# =========================================================
# 第三步：板块景气度（申万指数）
# =========================================================
def step3_prosperity():
    log("========== 第三步：板块景气度 ==========")
    sw_list = [
        ('801081.SI', '半导体'),
        ('801082.SI', '元件'),
        ('801085.SI', '电子化学品'),
    ]
    for sw_code, sw_name in sw_list:
        try:
            df = pro.sw_daily(ts_code=sw_code, start_date=START_DATE, end_date=TODAY)
            if df is not None and len(df) > 0:
                df['name'] = sw_name
                save_data(df, f'batch5_sw_{sw_name}')
                log(f"  ✅ 申万{sw_name}: {len(df)} 行")
            time.sleep(2)
        except Exception as e:
            log(f"  ❌ 申万{sw_name}: {str(e)[:60]}")
    
    log("  -- 北向资金全市场 --")
    try:
        hsgt = pro.moneyflow_hsgt(start_date='20260601', end_date=TODAY)
        if hsgt is not None and len(hsgt) > 0:
            save_data(hsgt, 'batch5_hsgt_monthly')
            log(f"  ✅ 北向全市场: {len(hsgt)} 行")
    except Exception as e:
        log(f"  ❌ 北向全市场: {str(e)[:60]}")

# =========================================================
# 第四步：估值（按 trade_date 批量，1次/60秒）
# =========================================================
def step4_valuation():
    log("========== 第四步：估值指标（按日期批量，1次/60s） ==========")
    log(f"  需要 {len(TRADE_DATES)} 天，预计 {len(TRADE_DATES)} 分钟")
    
    all_val = []
    for i, td in enumerate(TRADE_DATES):
        try:
            df = pro.daily_basic(trade_date=td,
                fields='ts_code,trade_date,close,pe,pe_ttm,pb,ps_ttm,dv_ttm,total_mv,circ_mv,turnover_rate,turnover_rate_f,volume_ratio')
            if df is not None and len(df) > 0:
                df = df[df['ts_code'].isin(ALL_CODES)].copy()
                if len(df) > 0:
                    df['name'] = df['ts_code'].map(NAME_MAP)
                    all_val.append(df)
                if (i+1) % 5 == 0 or i == 0 or i == len(TRADE_DATES)-1:
                    log(f"  进度 {i+1}/{len(TRADE_DATES)} | {td}: 命中 {len(df)} 行")
            time.sleep(60)
        except Exception as e:
            log(f"  ❌ {td}: {str(e)[:60]}")
            time.sleep(60)
    
    val = pd.concat(all_val, ignore_index=True) if all_val else pd.DataFrame()
    if len(val) > 0:
        val['trade_date'] = val['trade_date'].astype(str)
        save_data(val, 'batch2_valuation')

# =========================================================
# 第五步：资金流（moneyflow 1次/分钟，按 ts_code 拉）
# =========================================================
def step5_moneyflow():
    log("========== 第五步：资金流（按个股 1次/60s） ==========")
    all_mf = []
    for i, (code, name) in enumerate(STOCKS.items()):
        try:
            df = pro.moneyflow(ts_code=code, start_date='20260601', end_date=TODAY)
            if df is not None and len(df) > 0:
                df['name'] = name
                df['code'] = code
                all_mf.append(df)
                log(f"  {i+1}/{len(STOCKS)} {code} {name}: {len(df)} 行")
            time.sleep(60)
        except Exception as e:
            log(f"  ❌ {code} {name}: {str(e)[:60]}")
            time.sleep(60)
    
    mf = pd.concat(all_mf, ignore_index=True) if all_mf else pd.DataFrame()
    if len(mf) > 0:
        save_data(mf, 'batch4_moneyflow')

# =========================================================
# 第六步：合同负债（balancesheet 1次/分钟）
# =========================================================
def step6_contract_liab():
    log("========== 第六步：合同负债（按个股 1次/60s） ==========")
    all_cl = []
    for i, (code, name) in enumerate(STOCKS.items()):
        try:
            df = pro.balancesheet(ts_code=code, start_date='20240101', end_date=TODAY,
                fields='ts_code,end_date,ann_date,contract_liab,advance_receipts,inventory,accounts_rece,accounts_pay,total_assets,total_cur_assets')
            if df is not None and len(df) > 0:
                df['name'] = name
                df['code'] = code
                all_cl.append(df)
                log(f"  {i+1}/{len(STOCKS)} {code} {name}: {len(df)} 行")
            time.sleep(60)
        except Exception as e:
            log(f"  ❌ {code} {name}: {str(e)[:60]}")
            time.sleep(60)
    
    cl = pd.concat(all_cl, ignore_index=True) if all_cl else pd.DataFrame()
    if len(cl) > 0:
        save_data(cl, 'batch6_contract_liab')

# =========================================================
def main():
    log(f"🚀 开始抓取（{START_DATE} ~ {TODAY}）")
    log(f"标的池: {len(STOCKS)} 只个股 + {len(ETFs)} 只ETF + {len(INDICES)} 个指数")
    log(f"交易日数: {len(TRADE_DATES)} 天")
    
    # 不限流批次先跑
    step1_etf_index_quotes()  # 补 ETF/指数
    step2_financials()        # 财务（2s 间隔）
    step3_prosperity()        # 板块（2s 间隔）
    
    # 限流批次最后跑（60秒间隔）
    step4_valuation()         # 估值 ~37分钟
    step5_moneyflow()         # 资金流 ~18分钟
    step6_contract_liab()     # 合同负债 ~18分钟
    
    log("="*50)
    log("✅ 全部完成")

if __name__ == '__main__':
    main()
