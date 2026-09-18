#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare 补充核验（绕开 1次/分钟 与单标的限制）
策略：index_daily / daily_basic 用 trade_date 拉全市场，一次调用取全，再本地筛选。
用途：为《华为昇腾链圆桌报告（优化版）》提供估值与指数交叉验证
输出：stdout 摘要 + data/tushare_20260918_extra.json
"""
import os, json, time
import tushare as ts

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()
OUT = {}

def safe(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception as e:
        print(f'    [ERR] {str(e)[:150]}')
        return None

# ---------- 1. 指数：按交易日拉全部 ----------
print('=== 1. 指数（按 trade_date 全量拉取）===')
IDX = {'000001.SH': '上证指数', '399001.SZ': '深证成指', '399006.SZ': '创业板指',
       '000688.SH': '科创50', '899050.BJ': '北证50'}
idx_out = {}
for date in ('20260918', '20260917'):
    df = safe(pro.index_daily, trade_date=date)
    if df is not None and len(df):
        print(f'  {date}: 指数 {len(df)} 条')
        for code, name in IDX.items():
            hit = df[df['ts_code'] == code]
            if len(hit):
                r = hit.iloc[0]
                idx_out.setdefault(name, {})[date] = {
                    'close': float(r['close']), 'pct_chg': float(r['pct_chg']),
                    'amount_yi': round(float(r['amount']) / 1e5, 1),
                    'open': float(r['open']), 'high': float(r['high']), 'low': float(r['low'])}
                print(f'    {name:8s} {r["close"]:>10.2f}  {r["pct_chg"]:>+7.2f}%  成交 {float(r["amount"])/1e5:.0f}亿')
            else:
                print(f'    {name}: NOT FOUND')
    else:
        print(f'  {date}: NO DATA')
    time.sleep(62)  # 该接口 1次/分钟
OUT['index'] = idx_out

# ---------- 2. 估值：按交易日拉全部 ----------
print('\n=== 2. 估值 daily_basic（按 trade_date 全量拉取）===')
WATCH = {
    '002185.SZ': '华天科技', '600584.SH': '长电科技', '002156.SZ': '通富微电',
    '300308.SZ': '中际旭创', '300502.SZ': '新易盛', '300394.SZ': '天孚通信',
    '000988.SZ': '华工科技', '002463.SZ': '沪电股份', '000034.SZ': '神州数码',
    '000628.SZ': '高新发展', '688981.SH': '中芯国际', '002371.SZ': '北方华创',
    '688825.SH': '长鑫科技', '600105.SH': '永鼎股份', '000636.SZ': '风华高科',
    '002261.SZ': '拓维信息', '688629.SH': '华丰科技', '300059.SZ': '东方财富',
    '300750.SZ': '宁德时代', '600487.SH': '亨通光电',
}
val_out = {}
df = safe(pro.daily_basic, trade_date='20260918')
if df is not None and len(df):
    print(f'  20260918: 全市场 {len(df)} 条')
    for code, name in WATCH.items():
        hit = df[df['ts_code'] == code]
        if len(hit):
            r = hit.iloc[0]
            def fv(k):
                v = r[k] if k in r.index else None
                return float(v) if v is not None and v == v else None
            val_out[name] = {'code': code, 'pe_ttm': fv('pe_ttm'), 'pb': fv('pb'),
                             'ps_ttm': fv('ps_ttm'), 'dv_ttm': fv('dv_ttm'),
                             'total_mv_yi': round(fv('total_mv') / 1e4, 1) if fv('total_mv') else None,
                             'circ_mv_yi': round(fv('circ_mv') / 1e4, 1) if fv('circ_mv') else None,
                             'turnover_rate': fv('turnover_rate')}
            v = val_out[name]
            print(f'    {name:6s} PE(TTM) {str(v["pe_ttm"]):>9s}  PB {str(v["pb"]):>7s}  '
                  f'市值 {v["total_mv_yi"]}亿  换手 {v["turnover_rate"]}%')
        else:
            print(f'    {name}: NOT FOUND')
else:
    print('  NO DATA')
OUT['valuation'] = val_out

with open('data/tushare_20260918_extra.json', 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
print(f'\n[OK] 已保存 data/tushare_20260918_extra.json | 指数 {len(idx_out)} | 估值 {len(val_out)}')
