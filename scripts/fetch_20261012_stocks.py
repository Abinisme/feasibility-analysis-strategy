#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-10-12 个股全量补齐（腾讯行情批量，绕开 tushare 1次/小时限流）
字段: 名称/收盘/昨收/开盘/最高/最低/涨跌幅/成交额/换手/PE/PB/流通市值/总市值/涨停价/跌停价/量比
输出: data/20261012/stocks_qq.csv + stocks_merged.csv + summary2.json
"""
import os, json, time, warnings
warnings.filterwarnings('ignore')
import urllib.request
import pandas as pd
import tushare as ts

BASE = '/Users/yntwt/feasibility-analysis-strategy'
OUT = f'{BASE}/data/20261012'
DATE = '20261012'
os.makedirs(OUT, exist_ok=True)

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()

# ---------- 1. 股票清单（tushare daily 已落盘 5561 只，含交易所后缀） ----------
DP = f'{OUT}/daily_tushare.csv'
if os.path.exists(DP):
    tdaily = pd.read_csv(DP, dtype={'trade_date': str})
    print(f'[OK] 读取 daily_tushare.csv {len(tdaily)} 只')
else:
    tdaily = pro.daily(trade_date=DATE)
    tdaily.to_csv(DP, index=False, encoding='utf-8-sig')
    print(f'[OK] tushare daily {len(tdaily)} 行')
all_codes = tdaily['ts_code'].tolist()

# ---------- 1b. 行业映射（新浪49行业成分股，绕开 stock_basic 限流） ----------
print('\n=== 行业映射（新浪行业成分）===')
import akshare as ak
imap = {}
try:
    sp = ak.stock_sector_spot(indicator='新浪行业')
    sp.to_csv(f'{OUT}/board_industry_sina.csv', index=False, encoding='utf-8-sig')
    for _, r in sp.iterrows():
        try:
            d = ak.stock_sector_detail(sector=r['label'])
            for c in d['code']:
                imap[str(c).zfill(6)] = r['板块']
        except Exception as e:
            print(f"  [ERR] {r['板块']}: {str(e)[:60]}")
    print(f'[OK] 行业映射 {len(imap)} 只 | 覆盖行业 {len(set(imap.values()))}')
except Exception as e:
    print(f'[ERR] 新浪行业: {str(e)[:120]}')

# ---------- 3. 腾讯行情批量 ----------
print('\n=== 腾讯行情批量拉取 ===')

def to_qq(c):
    num, ex = c.split('.')
    return {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[ex] + num

codes = [to_qq(c) for c in all_codes]
B = 400
rows, fail = [], 0
for i in range(0, len(codes), B):
    url = 'http://qt.gtimg.cn/q=' + ','.join(codes[i:i + B])
    try:
        raw = urllib.request.urlopen(url, timeout=15).read().decode('gbk')
    except Exception as e:
        fail += 1
        print(f'  [ERR] batch@{i}: {str(e)[:80]}')
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
        code, ex = f[2], None
        pre = f[0]
        exmap = {'1': 'SH', '51': 'SZ', '62': 'BJ'}
        ex = exmap.get(pre, '?')
        rows.append({
            'ts_code': f'{code}.{ex}', 'name': f[1], 'close': gf(3), 'pre_close': gf(4),
            'open': gf(5), 'vol_hand': gf(6), 'ts': f[30] if len(f) > 30 else '',
            'change': gf(31), 'pct_chg': gf(32), 'high': gf(33), 'low': gf(34),
            'amount_wan': gf(37), 'turnover_rate': gf(38), 'pe_ttm': gf(39),
            'amplitude': gf(43), 'circ_mv_yi': gf(44), 'total_mv_yi': gf(45), 'pb': gf(46),
            'limit_up': gf(47), 'limit_down': gf(48), 'vol_ratio': gf(49),
        })
    if (i // B) % 4 == 0:
        print(f'  进度 {min(i + B, len(codes))}/{len(codes)}')
    time.sleep(0.12)

df = pd.DataFrame(rows)
df['amount_yi'] = (df['amount_wan'] / 1e4).round(2)
df['suspended'] = (df['vol_hand'] == 0) | (df['ts'].str.contains('0900', na=False))
df = df.drop_duplicates('ts_code').reset_index(drop=True)
print(f'[OK] 腾讯行情 {len(df)} 只 | 失败批 {fail}')
df.to_csv(f'{OUT}/stocks_qq.csv', index=False, encoding='utf-8-sig')

# ---------- 4. 合并行业 + tushare 行情交叉 ----------
mg = df.copy()
mg['code6'] = mg['ts_code'].str.split('.').str[0]
mg['industry'] = mg['code6'].map(imap).fillna('未分类')
mg = mg.merge(tdaily[['ts_code', 'pre_close', 'pct_chg', 'amount']].rename(
    columns={'pre_close': 'ts_pre_close', 'pct_chg': 'ts_pct_chg', 'amount': 'ts_amount'}),
    on='ts_code', how='left')
mg.to_csv(f'{OUT}/stocks_merged.csv', index=False, encoding='utf-8-sig')

live = mg[~mg['suspended']].copy()
print(f'  有效交易 {len(live)} 只 | 停牌 {int(mg["suspended"].sum())} 只')

# ---------- 5. 涨停/跌停判定（收盘价=涨跌停价，精确口径） ----------
EPS = 0.005
live['is_limit_up'] = (live['limit_up'] > 0) & ((live['close'] - live['limit_up']).abs() < EPS)
live['is_limit_down'] = (live['limit_down'] > 0) & ((live['close'] - live['limit_down']).abs() < EPS)
# 炸板股：最高价触及涨停但收盘未封住
live['touched_limit'] = (live['limit_up'] > 0) & ((live['high'] - live['limit_up']).abs() < EPS)
live['failed_limit'] = live['touched_limit'] & ~live['is_limit_up']

n_up = int((live['pct_chg'] > 0).sum())
n_dn = int((live['pct_chg'] < 0).sum())
n_flat = int((live['pct_chg'] == 0).sum())
lu = int(live['is_limit_up'].sum())
ld = int(live['is_limit_down'].sum())
fl = int(live['failed_limit'].sum())
tot_limit = lu + fl

stats = {
    'date': DATE,
    'total_live': len(live), 'up': n_up, 'down': n_dn, 'flat': n_flat,
    'up_ratio': round(n_up / len(live) * 100, 1),
    'mean_pct': round(float(live['pct_chg'].mean()), 2),
    'median_pct': round(float(live['pct_chg'].median()), 2),
    'amount_yi_total': round(float(live['amount_yi'].sum()), 1),
    'limit_up': lu, 'limit_down': ld, 'failed_limit(炸板)': fl,
    'seal_rate(封板率)': round(lu / tot_limit * 100, 1) if tot_limit else None,
    'pct_ge5': int((live['pct_chg'] >= 5).sum()), 'pct_le5': int((live['pct_chg'] <= -5).sum()),
    'pct_ge9': int((live['pct_chg'] >= 9).sum()), 'pct_le9': int((live['pct_chg'] <= -9).sum()),
    'amount_ge20yi': int((live['amount_yi'] >= 20).sum()),
    'mv_le50yi_share': round(float((live['total_mv_yi'] <= 50).mean() * 100), 1),
}
print('\n=== 市场概况 ===')
for k, v in stats.items():
    print(f'  {k}: {v}')

# 涨停股清单
lu_df = live[live['is_limit_up']].sort_values(['industry', 'amount_yi'], ascending=[True, False])
lu_df[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'turnover_rate', 'total_mv_yi']] \
    .to_csv(f'{OUT}/limit_up_list.csv', index=False, encoding='utf-8-sig')
ld_df = live[live['is_limit_down']].sort_values('amount_yi', ascending=False)
ld_df[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'total_mv_yi']] \
    .to_csv(f'{OUT}/limit_down_list.csv', index=False, encoding='utf-8-sig')

# 行业聚合
ind = live.groupby('industry').agg(
    n=('ts_code', 'count'), mean_pct=('pct_chg', 'mean'), median_pct=('pct_chg', 'median'),
    amount_yi=('amount_yi', 'sum'), up=('pct_chg', lambda s: int((s > 0).sum())),
    limit_up=('is_limit_up', 'sum')
).round(2).sort_values('mean_pct', ascending=False)
ind.to_csv(f'{OUT}/industry_agg.csv', encoding='utf-8-sig')

stats['industry_top12'] = ind.head(12).reset_index().to_dict('records')
stats['industry_bottom12'] = ind.tail(12).reset_index().to_dict('records')
stats['limit_up_by_industry'] = ind[ind['limit_up'] > 0].sort_values('limit_up', ascending=False) \
    .reset_index()[['industry', 'limit_up', 'mean_pct']].to_dict('records')
stats['top_gainers'] = live.nlargest(25, 'pct_chg')[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'total_mv_yi']].to_dict('records')
stats['top_losers'] = live.nsmallest(25, 'pct_chg')[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi', 'total_mv_yi']].to_dict('records')
stats['amt_top25'] = live.nlargest(25, 'amount_yi')[['ts_code', 'name', 'industry', 'close', 'pct_chg', 'amount_yi']].to_dict('records')

with open(f'{OUT}/summary2.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print('\n=== 行业涨幅前10 ===')
for r in stats['industry_top12'][:10]:
    print(f"  {r['industry']:10s} {r['mean_pct']:>+6.2f}%  额{r['amount_yi']:>7.0f}亿  涨停{int(r['limit_up'])}")
print('=== 行业涨幅后5 ===')
for r in stats['industry_bottom12'][-5:]:
    print(f"  {r['industry']:10s} {r['mean_pct']:>+6.2f}%  额{r['amount_yi']:>7.0f}亿  涨停{int(r['limit_up'])}")
print('\n=== 涨停股行业分布 Top12 ===')
for r in stats['limit_up_by_industry'][:12]:
    print(f"  {r['industry']:10s} 涨停{int(r['limit_up'])}家  平均{r['mean_pct']:+.2f}%")
print(f'\n[DONE] {OUT}')
