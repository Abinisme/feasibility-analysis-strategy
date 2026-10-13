#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日全量数据拉取（参数化版，替代 fetch_YYYYMMDD_*.py）
用法: python3 scripts/fetch_daily.py 20261013 [--skip-qq]
通道: tushare(daily) + 腾讯行情(个股/指数批量) + 同花顺(板块/资金流) + 交易所(两融)
输出: data/{DATE}/
"""
import os, sys, json, time, warnings
warnings.filterwarnings('ignore')
import urllib.request
import pandas as pd
import tushare as ts

BASE = '/Users/yntwt/feasibility-analysis-strategy'
DATE = sys.argv[1] if len(sys.argv) > 1 else time.strftime('%Y%m%d')
SKIP_QQ = '--skip-qq' in sys.argv
OUT = f'{BASE}/data/{DATE}'
os.makedirs(OUT, exist_ok=True)
CACHE = f'{BASE}/data/_cache'
os.makedirs(CACHE, exist_ok=True)

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()
SUMMARY = {'date': DATE}


def save(df, name):
    p = f'{OUT}/{name}.csv'
    df.to_csv(p, index=False, encoding='utf-8-sig')
    print(f'  [SAVE] {name}.csv ({len(df)}行)')
    return p


# ================= M1. tushare 全市场日线 =================
print(f'=== M1. tushare daily {DATE} ===')
d = pro.daily(trade_date=DATE)
save(d, 'daily_tushare')
print(f'  [OK] {len(d)} 只')

# ================= M2. 腾讯行情批量（个股全量） =================
if not SKIP_QQ:
    print('\n=== M2. 腾讯行情批量 ===')
    def to_qq(c):
        num, ex = c.split('.')
        return {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[ex] + num

    codes = [to_qq(c) for c in d['ts_code']]
    B, rows, fail = 400, [], 0
    for i in range(0, len(codes), B):
        try:
            raw = urllib.request.urlopen(
                'http://qt.gtimg.cn/q=' + ','.join(codes[i:i + B]), timeout=15).read().decode('gbk')
        except Exception as e:
            fail += 1
            print(f'  [ERR] batch@{i}: {str(e)[:70]}')
            continue
        for line in raw.strip().split(';'):
            if '="' not in line:
                continue
            f = line.split('="')[1].strip('"').split('~')
            if len(f) < 50:
                continue
            def gf(k):
                try:
                    return float(f[k])
                except Exception:
                    return None
            ex = {'1': 'SH', '51': 'SZ', '62': 'BJ'}.get(f[0], '?')
            rows.append({'ts_code': f'{f[2]}.{ex}', 'name': f[1], 'close': gf(3), 'pre_close': gf(4),
                         'open': gf(5), 'vol_hand': gf(6), 'ts': f[30] if len(f) > 30 else '',
                         'change': gf(31), 'pct_chg': gf(32), 'high': gf(33), 'low': gf(34),
                         'amount_wan': gf(37), 'turnover_rate': gf(38), 'pe_ttm': gf(39),
                         'amplitude': gf(43), 'circ_mv_yi': gf(44), 'total_mv_yi': gf(45), 'pb': gf(46),
                         'limit_up': gf(47), 'limit_down': gf(48), 'vol_ratio': gf(49)})
        time.sleep(0.12)
    qq = pd.DataFrame(rows).drop_duplicates('ts_code')
    qq['amount_yi'] = (qq['amount_wan'] / 1e4).round(2)
    qq['suspended'] = (qq['vol_hand'] == 0)
    save(qq, 'stocks_qq')
    print(f'  [OK] {len(qq)} 只 | 失败批 {fail}')

# ================= M3. 行业映射（新浪，缓存） =================
print('\n=== M3. 行业映射 ===')
import akshare as ak
IMAP_P = f'{CACHE}/industry_map_sina.csv'
if os.path.exists(IMAP_P):
    im = pd.read_csv(IMAP_P, dtype={'code': str})
    imap = dict(zip(im['code'].str.zfill(6), im['industry']))
    print(f'  [CACHE] 行业映射 {len(imap)} 只')
else:
    imap = {}
    sp = ak.stock_sector_spot(indicator='新浪行业')
    for _, r in sp.iterrows():
        try:
            dd = ak.stock_sector_detail(sector=r['label'])
            for c in dd['code']:
                imap[str(c).zfill(6)] = r['板块']
        except Exception:
            pass
    pd.DataFrame({'code': list(imap.keys()), 'industry': list(imap.values())}).to_csv(
        IMAP_P, index=False, encoding='utf-8-sig')
    print(f'  [OK] 行业映射 {len(imap)} 只')

# ================= M4. 合并 + 涨跌停判定 =================
print('\n=== M4. 合并与涨跌停判定 ===')
qp = f'{OUT}/stocks_qq.csv'
if os.path.exists(qp):
    mg = pd.read_csv(qp, dtype={'code6': str})
    mg['code6'] = mg['ts_code'].str.split('.').str[0]
else:
    mg = d.copy()
    mg['name'] = ''
    mg['code6'] = mg['ts_code'].str.split('.').str[0]
mg['industry'] = mg['code6'].map(imap).fillna('未分类')
mg = mg.merge(d[['ts_code', 'pre_close', 'pct_chg', 'amount']].rename(
    columns={'pre_close': 'ts_pre_close', 'pct_chg': 'ts_pct_chg', 'amount': 'ts_amount'}),
    on='ts_code', how='left')
save(mg, 'stocks_merged')

live = mg[~mg['suspended'].fillna(False)].copy() if 'suspended' in mg else mg.copy()
EPS = 0.005
live['is_limit_up'] = (live['limit_up'] > 0) & ((live['close'] - live['limit_up']).abs() < EPS)
live['is_limit_down'] = (live['limit_down'] > 0) & ((live['close'] - live['limit_down']).abs() < EPS)
live['touched_limit'] = (live['limit_up'] > 0) & ((live['high'] - live['limit_up']).abs() < EPS)
live['failed_limit'] = live['touched_limit'] & ~live['is_limit_up']

lu, ld, fl = int(live['is_limit_up'].sum()), int(live['is_limit_down'].sum()), int(live['failed_limit'].sum())
tot = lu + fl
stats = {
    'date': DATE, 'total_live': len(live),
    'up': int((live['pct_chg'] > 0).sum()), 'down': int((live['pct_chg'] < 0).sum()),
    'flat': int((live['pct_chg'] == 0).sum()),
    'mean_pct': round(float(live['pct_chg'].mean()), 2),
    'median_pct': round(float(live['pct_chg'].median()), 2),
    'amount_yi_total': round(float(live['amount_yi'].sum()), 1),
    'limit_up': lu, 'limit_down': ld, 'failed_limit': fl,
    'limit_up_exST': int(live[live['is_limit_up'] & ~live['name'].astype(str).str.contains('ST')].shape[0]),
    'limit_down_exST': int(live[live['is_limit_down'] & ~live['name'].astype(str).str.contains('ST')].shape[0]),
    'seal_rate': round(lu / tot * 100, 1) if tot else None,
    'pct_ge5': int((live['pct_chg'] >= 5).sum()), 'pct_le5': int((live['pct_chg'] <= -5).sum()),
    'amount_ge20yi': int((live['amount_yi'] >= 20).sum()),
}
live[live['is_limit_up']].sort_values('amount_yi', ascending=False)[
    ['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'turnover_rate', 'total_mv_yi', 'limit_up']] \
    .to_csv(f'{OUT}/limit_up_list.csv', index=False, encoding='utf-8-sig')
live[live['is_limit_down']].sort_values('amount_yi', ascending=False)[
    ['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'total_mv_yi']] \
    .to_csv(f'{OUT}/limit_down_list.csv', index=False, encoding='utf-8-sig')
live[live['failed_limit']].sort_values('amount_yi', ascending=False)[
    ['ts_code', 'name', 'industry', 'close', 'pct_chg', 'high', 'limit_up', 'amount_yi']] \
    .to_csv(f'{OUT}/failed_limit_list.csv', index=False, encoding='utf-8-sig')

ind = live.groupby('industry').agg(
    n=('ts_code', 'count'), mean_pct=('pct_chg', 'mean'), median_pct=('pct_chg', 'median'),
    amount_yi=('amount_yi', 'sum'), up=('pct_chg', lambda s: int((s > 0).sum())),
    limit_up=('is_limit_up', 'sum')).round(2).sort_values('mean_pct', ascending=False)
ind.to_csv(f'{OUT}/industry_agg.csv', encoding='utf-8-sig')

stats['industry_top12'] = ind.head(12).reset_index().to_dict('records')
stats['industry_bottom12'] = ind.tail(12).reset_index().to_dict('records')
stats['limit_up_by_industry'] = ind[ind['limit_up'] > 0].sort_values(
    'limit_up', ascending=False).reset_index()[['industry', 'limit_up', 'mean_pct']].to_dict('records')
stats['top_gainers'] = live.nlargest(30, 'pct_chg')[
    ['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'total_mv_yi']].to_dict('records')
stats['top_losers'] = live.nsmallest(30, 'pct_chg')[
    ['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'total_mv_yi']].to_dict('records')
stats['amt_top30'] = live.nlargest(30, 'amount_yi')[
    ['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi']].to_dict('records')
print(f"  涨{stats['up']}/跌{stats['down']} | 涨停{lu}(剔ST{stats['limit_up_exST']}) 跌停{ld} 炸板{fl} 封板率{stats['seal_rate']}%")
print('  行业前5:', ' / '.join(f"{r['industry']}{r['mean_pct']:+.2f}%" for r in stats['industry_top12'][:5]))
print('  行业后5:', ' / '.join(f"{r['industry']}{r['mean_pct']:+.2f}%" for r in stats['industry_bottom12'][-5:]))

# ================= M5. 指数（腾讯） =================
print('\n=== M5. 指数 ===')
IDX = {'sh000001': '上证指数', 'sz399001': '深证成指', 'sz399006': '创业板指', 'sh000688': '科创50',
       'bj899050': '北证50', 'sh000300': '沪深300', 'sh000905': '中证500', 'sh000852': '中证1000',
       'sh000016': '上证50', 'sz399303': '国证2000', 'sh000510': '中证A500', 'sz399330': '深证100'}
try:
    raw = urllib.request.urlopen('http://qt.gtimg.cn/q=' + ','.join(IDX), timeout=12).read().decode('gbk')
    idx_rows = {}
    for line in raw.strip().split(';'):
        if '="' not in line:
            continue
        code = line.split('=')[0].replace('v_', '').strip()
        f = line.split('="')[1].strip('"').split('~')
        if len(f) < 50:
            continue
        idx_rows[IDX.get(code, code)] = {'code': code, 'name': f[1], 'close': float(f[3]), 'pre_close': float(f[4]),
                                         'open': float(f[5]), 'change': float(f[31]), 'pct_chg': float(f[32]),
                                         'high': float(f[33]), 'low': float(f[34]),
                                         'amount_yi': round(float(f[37]) / 1e4, 2), 'turnover': float(f[38]),
                                         'amplitude': float(f[43]), 'vol_ratio': float(f[49]) if f[49] else None}
    save(pd.DataFrame(idx_rows).T, 'indices_tencent')
    SUMMARY['indices'] = idx_rows
    for k, v in idx_rows.items():
        print(f"  {k:8s} {v['close']:>10.2f} {v['pct_chg']:>+7.2f}%  额{v['amount_yi']:>8.1f}亿 量比{v['vol_ratio']}")
except Exception as e:
    print(f'  [ERR] 指数: {str(e)[:120]}')

# ================= M6. 同花顺板块 + 资金流 =================
print('\n=== M6. 板块与资金流 ===')
def atry(name, fn, fname):
    try:
        x = fn()
        save(x, fname)
        return x
    except Exception as e:
        print(f'  [ERR] {name}: {str(e)[:100]}')
        return None

atry('行业板块90', lambda: ak.stock_board_industry_summary_ths(), 'board_industry_ths')
atry('概念摘要50', lambda: ak.stock_board_concept_summary_ths(), 'board_concept_summary_ths')
atry('行业资金流', lambda: ak.stock_fund_flow_industry(symbol='即时'), 'fundflow_industry_ths')
atry('概念资金流', lambda: ak.stock_fund_flow_concept(symbol='即时'), 'fundflow_concept_ths')
atry('个股资金流', lambda: ak.stock_fund_flow_individual(symbol='即时'), 'fundflow_individual_ths')

# ================= M7. 两融 =================
print('\n=== M7. 两融 ===')
try:
    m = ak.stock_margin_sse(start_date='20260920', end_date=DATE)
    save(m, 'margin_sse')
    SUMMARY['margin_sse'] = m.head(3).to_dict('records')
except Exception as e:
    print(f'  [ERR] 上交所: {str(e)[:90]}')

with open(f'{OUT}/summary.json', 'w', encoding='utf-8') as f:
    json.dump(SUMMARY, f, ensure_ascii=False, indent=2)
print(f'\n[DONE] {OUT}')
