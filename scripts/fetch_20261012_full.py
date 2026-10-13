#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-10-12（周一）A股全量数据拉取 —— 任务1 · 通道A/B/C/D
通道A tushare   : 指数(index_daily 全量1186) / 个股(daily 全市场) / 估值(daily_basic) / 基础信息(stock_basic)
通道B 同花顺    : 行业板块90 / 概念板块387 / 概念摘要50 / 板块资金流 / 个股资金流5212
通道C 腾讯行情  : 主要指数精确行情（开高低收/量比/振幅，比 tushare 多量比）
通道D 上交所    : 两融余额
输出: data/20261012/
"""
import os, json, time, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import tushare as ts

BASE = '/Users/yntwt/feasibility-analysis-strategy'
OUT = f'{BASE}/data/20261012'
os.makedirs(OUT, exist_ok=True)
DATE = '20261012'

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()


def save(df, name):
    df.to_csv(f'{OUT}/{name}.csv', index=False, encoding='utf-8-sig')
    print(f'  [SAVE] {name}.csv ({len(df)}行 x {len(df.columns)}列)')


def jdump(obj, name):
    with open(f'{OUT}/{name}.json', 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f'  [SAVE] {name}.json')


SUMMARY = {'date': DATE}

# ============================================================
# M1. 主要指数（腾讯行情，含量比/振幅；tushare 交叉验证）
# ============================================================
print('=== M1. 主要指数（腾讯行情）===')
IDX = {
    'sh000001': '上证指数', 'sz399001': '深证成指', 'sz399006': '创业板指',
    'sh000688': '科创50', 'bj899050': '北证50', 'sh000300': '沪深300',
    'sh000905': '中证500', 'sh000852': '中证1000', 'sh000016': '上证50',
    'sz399303': '国证2000', 'sh000510': '中证A500', 'sz399330': '深证100',
}
try:
    import urllib.request
    url = 'http://qt.gtimg.cn/q=' + ','.join(IDX.keys())
    raw = urllib.request.urlopen(url, timeout=12).read().decode('gbk')
    idx_rows = {}
    for line in raw.strip().split(';'):
        if '="' not in line:
            continue
        code = line.split('=')[0].replace('v_', '').strip()
        f = line.split('="')[1].strip('"').split('~')
        if len(f) < 50:
            continue
        idx_rows[IDX.get(code, code)] = {
            'code': code, 'name': f[1], 'close': float(f[3]), 'pre_close': float(f[4]),
            'open': float(f[5]), 'change': float(f[31]), 'pct_chg': float(f[32]),
            'high': float(f[33]), 'low': float(f[34]),
            'amount_yi': round(float(f[37]) / 1e4, 2), 'turnover': float(f[38]),
            'amplitude': float(f[43]), 'vol_ratio': float(f[49]) if f[49] else None,
        }
    df_idx = pd.DataFrame(idx_rows).T
    save(df_idx, 'indices_tencent')
    SUMMARY['indices'] = idx_rows
    for k, v in idx_rows.items():
        print(f"    {k:8s} {v['close']:>10.2f} {v['pct_chg']:>+7.2f}%  额{v['amount_yi']:>9.1f}亿  量比{v['vol_ratio']}")
except Exception as e:
    print(f'  [ERR] 腾讯指数: {str(e)[:150]}')

# tushare 指数全量存档
try:
    df_ix = pro.index_daily(trade_date=DATE)
    save(df_ix, 'index_daily_full')
    print(f'  [OK] tushare index_daily 全量 {len(df_ix)} 个指数')
except Exception as e:
    print(f'  [ERR] index_daily: {str(e)[:150]}')

# ============================================================
# M2. 个股全量：行情 + 估值 + 行业分类（合并宽表）
# ============================================================
print('\n=== M2. 个股全量（daily + daily_basic + stock_basic）===')
try:
    d = pro.daily(trade_date=DATE)
    b = pro.daily_basic(trade_date=DATE)
    sb = pro.stock_basic(exchange='', list_status='L',
                         fields='ts_code,name,industry,market,list_date')
    sb2 = pro.stock_basic(exchange='', list_status='D', fields='ts_code,name')
    sb3 = pro.stock_basic(exchange='', list_status='P', fields='ts_code,name')
    names = pd.concat([sb, sb2, sb3]).drop_duplicates('ts_code')
    df = d.merge(b[['ts_code', 'turnover_rate', 'volume_ratio', 'pe_ttm', 'pb',
                    'total_mv', 'circ_mv', 'total_share', 'float_share']], on='ts_code', how='left')
    df = df.merge(names[['ts_code', 'name', 'industry', 'market', 'list_date']], on='ts_code', how='left')
    df['amount_yi'] = (df['amount'] / 1e5).round(2)          # 千元 -> 亿元
    df['total_mv_yi'] = (df['total_mv'] / 1e4).round(1)
    df['circ_mv_yi'] = (df['circ_mv'] / 1e4).round(1)
    df = df.sort_values('pct_chg', ascending=False).reset_index(drop=True)
    save(df, 'stocks_full')
    print(f'  [OK] 合并宽表 {len(df)} 只 | 行业覆盖 {df["industry"].notna().sum()}')
except Exception as e:
    print(f'  [ERR] 个股全量: {str(e)[:150]}')
    df = None

# ============================================================
# M3. 板块：同花顺行业/概念 + 新浪行业
# ============================================================
print('\n=== M3. 板块（同花顺 + 新浪）===')
import akshare as ak

def atry(name, fn, fname=None):
    try:
        x = fn()
        if fname:
            save(x, fname)
        print(f'  [OK] {name}: {len(x)} 行')
        return x
    except Exception as e:
        print(f'  [ERR] {name}: {str(e)[:120]}')
        return None

ths_ind = atry('同花顺行业板块90', lambda: ak.stock_board_industry_summary_ths(), 'board_industry_ths')
ths_sum = atry('同花顺概念摘要50', lambda: ak.stock_board_concept_summary_ths(), 'board_concept_summary_ths')
sina_ind = atry('新浪行业49', lambda: ak.stock_sector_spot(indicator='新浪行业'), 'board_industry_sina')

# ============================================================
# M4. 资金流：板块 + 个股（同花顺即时）
# ============================================================
print('\n=== M4. 资金流（同花顺）===')
ff_ind = atry('行业资金流90', lambda: ak.stock_fund_flow_industry(symbol='即时'), 'fundflow_industry_ths')
ff_con = atry('概念资金流387', lambda: ak.stock_fund_flow_concept(symbol='即时'), 'fundflow_concept_ths')
ff_stk = atry('个股资金流5212', lambda: ak.stock_fund_flow_individual(symbol='即时'), 'fundflow_individual_ths')

# ============================================================
# M5. 两融（上交所 + 深交所）
# ============================================================
print('\n=== M5. 两融余额 ===')
try:
    m_sse = ak.stock_margin_sse(start_date='20260915', end_date=DATE)
    save(m_sse, 'margin_sse')
    SUMMARY['margin_sse_latest'] = m_sse.iloc[0].to_dict() if len(m_sse) else None
    print(f'  [OK] 上交所两融 {len(m_sse)} 行')
except Exception as e:
    print(f'  [ERR] 上交所两融: {str(e)[:120]}')
try:
    m_szse = ak.stock_margin_szse(date=DATE)
    save(m_szse, 'margin_szse')
    print(f'  [OK] 深交所两融 {len(m_szse)} 行')
except Exception as e:
    print(f'  [ERR] 深交所两融: {str(e)[:120]}')

# ============================================================
# M6. 当日市场概况速览（基于 stocks_full 自算）
# ============================================================
print('\n=== M6. 市场概况自算 ===')
if df is not None:
    up = int((df['pct_chg'] > 0).sum())
    dn = int((df['pct_chg'] < 0).sum())
    flat = int((df['pct_chg'] == 0).sum())
    amt = float(df['amount_yi'].sum())
    stats = {
        'total': len(df), 'up': up, 'down': dn, 'flat': flat,
        'up_ratio': round(up / len(df) * 100, 1),
        'amount_yi_total': round(amt, 1),
        'median_pct': round(float(df['pct_chg'].median()), 2),
        'mean_pct': round(float(df['pct_chg'].mean()), 2),
        'up_gt5': int((df['pct_chg'] >= 5).sum()), 'down_lt5': int((df['pct_chg'] <= -5).sum()),
        'up_gt9': int((df['pct_chg'] >= 9).sum()), 'down_lt9': int((df['pct_chg'] <= -9).sum()),
        'top20': df.head(20)[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi']].to_dict('records'),
        'bottom20': df.tail(20)[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi']].to_dict('records'),
        'amt_top20': df.nlargest(20, 'amount_yi')[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi']].to_dict('records'),
        'mv_top20': df.nlargest(20, 'total_mv_yi')[['ts_code', 'name', 'close', 'pct_chg', 'total_mv_yi']].to_dict('records'),
    }
    # 行业聚合（tushare industry 口径）
    ind_agg = df.groupby('industry').agg(
        n=('ts_code', 'count'), mean_pct=('pct_chg', 'mean'),
        amount_yi=('amount_yi', 'sum'), up=('pct_chg', lambda s: int((s > 0).sum()))
    ).round(2).sort_values('mean_pct', ascending=False)
    ind_agg.to_csv(f'{OUT}/industry_agg_tushare.csv', encoding='utf-8-sig')
    stats['industry_top10'] = ind_agg.head(10).reset_index().to_dict('records')
    stats['industry_bottom10'] = ind_agg.tail(10).reset_index().to_dict('records')
    SUMMARY['market'] = stats
    print(f"  涨{up}/跌{dn}/平{flat} | 中位{stats['median_pct']}% | 总成交{amt:.0f}亿")
    print('  涨幅前5:', ' / '.join(f"{r['name']}{r['pct_chg']:+.1f}%" for r in stats['top20'][:5]))
    print('  行业前5:', ' / '.join(f"{r['industry']}{r['mean_pct']:+.2f}%" for r in stats['industry_top10'][:5]))

jdump(SUMMARY, 'summary')
print(f'\n[DONE] 输出目录 {OUT}')
