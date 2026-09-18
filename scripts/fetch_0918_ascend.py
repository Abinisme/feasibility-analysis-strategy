#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare 独立核验 2026-09-18 行情 / 估值 / 资金 / 涨跌停
用途：为《华为昇腾链圆桌报告（优化版）》提供第三方数据源交叉验证
输出：stdout 摘要 + data/tushare_20260918.json
"""
import os, json, time, sys
import tushare as ts

ts.set_token(os.environ['TUSHARE_TOKEN'])
pro = ts.pro_api()

D, PREV = '20260918', '20260917'
OUT = {}

def safe(fn, *a, **kw):
    for _ in range(2):
        try:
            df = fn(*a, **kw)
            return df
        except Exception as e:
            err = str(e)[:120]
            time.sleep(1.0)
    print(f'    [ERR] {err}')
    return None

# ---------- 1. 指数 ----------
IDX = {'000001.SH': '上证指数', '399001.SZ': '深证成指', '399006.SZ': '创业板指',
       '000688.SH': '科创50', '899050.BJ': '北证50'}
print('=== 1. 指数 9/18 ===')
idx_out = {}
for code, name in IDX.items():
    df = safe(pro.index_daily, ts_code=code, start_date=D, end_date=D)
    if df is not None and len(df):
        r = df.iloc[0]
        idx_out[name] = {'code': code, 'close': float(r['close']), 'pct_chg': float(r['pct_chg']),
                         'amount': float(r['amount']), 'vol': float(r['vol'])}
        print(f'  {name:8s} {r["close"]:>10.2f}  {r["pct_chg"]:>+7.2f}%  成交 {float(r["amount"])/1e5:.0f}亿')
    else:
        print(f'  {name}: NO DATA')
    time.sleep(0.32)
OUT['index'] = idx_out

# ---------- 2. 全市场涨跌分布（裁定 80 vs 78 家） ----------
print('\n=== 2. 全市场涨跌分布 9/18 ===')
breadth = {}
for tag, date in (('9/18', D), ('9/17', PREV)):
    df = safe(pro.daily, trade_date=date)
    if df is not None and len(df):
        df = df[df['close'].notna()]
        up = int((df['pct_chg'] > 0).sum())
        dn = int((df['pct_chg'] < 0).sum())
        fl = int((df['pct_chg'] == 0).sum())
        lim_up = int((df['pct_chg'] >= 9.8).sum())
        lim_dn = int((df['pct_chg'] <= -9.8).sum())
        amt = float(df['amount'].sum()) / 1e5  # 千元 -> 亿元
        breadth[tag] = {'total': len(df), 'up': up, 'down': dn, 'flat': fl,
                        'limit_up_approx': lim_up, 'limit_down_approx': lim_dn,
                        'amount_yi': round(amt, 1)}
        print(f'  {tag}: 总 {len(df)} | 涨 {up} / 跌 {dn} / 平 {fl} | '
              f'涨停(≥9.8%) {lim_up} / 跌停 {lim_dn} | 成交 {amt:.0f} 亿')
    else:
        print(f'  {tag}: NO DATA')
    time.sleep(0.5)
OUT['breadth'] = breadth

# 官方涨停口径
print('\n  -- limit_list_d 官方涨停/跌停口径 --')
for tag, date in (('9/18', D), ('9/17', PREV)):
    df = safe(pro.limit_list_d, trade_date=date, limit_type='U')
    if df is not None:
        breadth.setdefault(tag, {})['limit_up_official'] = len(df)
        print(f'  {tag} 涨停家数(官方) = {len(df)}')
    df2 = safe(pro.limit_list_d, trade_date=date, limit_type='D')
    if df2 is not None:
        breadth.setdefault(tag, {})['limit_down_official'] = len(df2)
        print(f'  {tag} 跌停家数(官方) = {len(df2)}')
    time.sleep(0.5)

# ---------- 3. 个股行情 ----------
STK = {
    '002185.SZ': '华天科技', '600584.SH': '长电科技', '002156.SZ': '通富微电',
    '300308.SZ': '中际旭创', '300502.SZ': '新易盛', '300394.SZ': '天孚通信',
    '000988.SZ': '华工科技', '600105.SH': '永鼎股份', '600487.SH': '亨通光电',
    '688825.SH': '长鑫科技', '600667.SH': '太极实业',
    '002463.SZ': '沪电股份', '002916.SZ': '深南电路', '600183.SH': '生益科技',
    '000034.SZ': '神州数码', '000628.SZ': '高新发展', '002261.SZ': '拓维信息',
    '688981.SH': '中芯国际', '002371.SZ': '北方华创', '300059.SZ': '东方财富',
    '300750.SZ': '宁德时代', '000158.SZ': '常山北明', '301236.SZ': '软通动力',
    '300570.SZ': '太辰光', '000636.SZ': '风华高科', '600206.SH': '有研新材',
    '600176.SH': '中国巨石', '002080.SZ': '中材科技',
}
print('\n=== 3. 个股 9/18 行情 ===')
stk_out = {}
for code, name in STK.items():
    df = safe(pro.daily, ts_code=code, start_date=D, end_date=D)
    if df is not None and len(df):
        r = df.iloc[0]
        stk_out[name] = {'code': code, 'close': float(r['close']), 'pct_chg': float(r['pct_chg']),
                         'amount_wan': float(r['amount']), 'vol': float(r['vol'])}
        print(f'  {name:6s} {r["close"]:>9.2f}  {r["pct_chg"]:>+7.2f}%')
    else:
        print(f'  {name}: NO DATA')
    time.sleep(0.32)
OUT['stock'] = stk_out

# ---------- 4. 估值 daily_basic ----------
print('\n=== 4. 估值 daily_basic 9/18 ===')
val_out = {}
for code, name in STK.items():
    df = safe(pro.daily_basic, ts_code=code, trade_date=D)
    if df is not None and len(df):
        r = df.iloc[0]
        val_out[name] = {
            'code': code,
            'pe_ttm': float(r['pe_ttm']) if r['pe_ttm'] == r['pe_ttm'] else None,
            'pb': float(r['pb']) if r['pb'] == r['pb'] else None,
            'ps_ttm': float(r['ps_ttm']) if r['ps_ttm'] == r['ps_ttm'] else None,
            'dv_ratio': float(r['dv_ratio']) if r['dv_ratio'] == r['dv_ratio'] else None,
            'total_mv_yi': round(float(r['total_mv']) / 1e4, 1) if r['total_mv'] == r['total_mv'] else None,
            'circ_mv_yi': round(float(r['circ_mv']) / 1e4, 1) if r['circ_mv'] == r['circ_mv'] else None,
            'turnover_rate': float(r['turnover_rate']) if r['turnover_rate'] == r['turnover_rate'] else None,
        }
        v = val_out[name]
        print(f'  {name:6s} PE(TTM) {str(v["pe_ttm"]):>9s}  PB {str(v["pb"]):>7s}  市值 {v["total_mv_yi"]}亿  换手 {v["turnover_rate"]}%')
    time.sleep(0.32)
OUT['valuation'] = val_out

# ---------- 5. 资金流 moneyflow ----------
print('\n=== 5. 资金流 moneyflow（争议核心：华天/长电/中际旭创）===')
mf_out = {}
for code, name in [('002185.SZ', '华天科技'), ('600584.SH', '长电科技'), ('300308.SZ', '中际旭创'),
                   ('300502.SZ', '新易盛'), ('002463.SZ', '沪电股份')]:
    df = safe(pro.moneyflow, ts_code=code, trade_date=D)
    if df is not None and len(df):
        r = df.iloc[0]
        net = (float(r['buy_lg_amount']) + float(r['buy_elg_amount'])
               - float(r['sell_lg_amount']) - float(r['sell_elg_amount']))
        mf_out[name] = {'code': code, 'net_lg_elg_wan': round(net, 0),
                        'buy_elg': float(r['buy_elg_amount']), 'sell_elg': float(r['sell_elg_amount']),
                        'buy_lg': float(r['buy_lg_amount']), 'sell_lg': float(r['sell_lg_amount']),
                        'net_mf_amount_wan': float(r['net_mf_amount'])}
        print(f'  {name:6s} 大+超大单净额 {net/1e4:>+8.2f} 亿 | net_mf_amount {float(r["net_mf_amount"])/1e4:>+8.2f} 亿')
    else:
        print(f'  {name}: NO DATA（可能积分不足）')
    time.sleep(0.4)
OUT['moneyflow'] = mf_out

# ---------- 6. 龙虎榜 ----------
print('\n=== 6. 龙虎榜 top_list 9/18 ===')
tl = safe(pro.top_list, trade_date=D)
if tl is not None and len(tl):
    hit = tl[tl['ts_code'].isin(['002185.SZ', '600584.SH', '300308.SZ'])]
    OUT['top_list_all_count'] = len(tl)
    tl_out = []
    for _, r in hit.iterrows():
        tl_out.append({'name': r['name'], 'code': r['ts_code'],
                       'net_amount_yi': round(float(r['net_amount']) / 1e8, 2),
                       'l_buy_yi': round(float(r['l_buy']) / 1e8, 2),
                       'l_sell_yi': round(float(r['l_sell']) / 1e8, 2)})
        print(f'  {r["name"]}: 龙虎榜净额 {float(r["net_amount"])/1e8:+.2f} 亿 '
              f'(买 {float(r["l_buy"])/1e8:.2f} / 卖 {float(r["l_sell"])/1e8:.2f})')
    OUT['top_list_focus'] = tl_out
    print(f'  全市场龙虎榜上榜 {len(tl)} 只')
else:
    print('  NO DATA（可能积分不足）')

# ---------- 7. 财报核验 ----------
print('\n=== 7. 财报 income / fina_indicator（2026H1）===')
FIN = {'002185.SZ': '华天科技', '600584.SH': '长电科技', '002156.SZ': '通富微电',
       '688825.SH': '长鑫科技', '000034.SZ': '神州数码', '688981.SH': '中芯国际',
       '002371.SZ': '北方华创'}
fin_out = {}
ti = 0
for code, name in FIN.items():
    inc = safe(pro.income, ts_code=code, period='20260630')
    ind = safe(pro.fina_indicator, ts_code=code, period='20260630')
    rec = {'code': code}
    if inc is not None and len(inc):
        r = inc.iloc[0]
        rec['revenue_yi'] = round(float(r['revenue']) / 1e8, 1) if r['revenue'] == r['revenue'] else None
        rec['n_income_attr_yi'] = round(float(r['n_income_attr_p']) / 1e8, 1) if r['n_income_attr_p'] == r['n_income_attr_p'] else None
    if ind is not None and len(ind):
        r = ind.iloc[0]
        for k, f in (('grossprofit_margin', 'gross_margin'), ('netprofit_margin', 'net_margin'),
                     ('roe', 'roe'), ('or_yoy', 'revenue_yoy'), ('netprofit_yoy', 'netprofit_yoy')):
            rec[f] = float(r[k]) if k in r and r[k] == r[k] else None
    fin_out[name] = rec
    print(f'  {name:6s} 营收 {rec.get("revenue_yi")}亿 | 归母 {rec.get("n_income_attr_yi")}亿 | '
          f'毛利率 {rec.get("gross_margin")}% | 营收同比 {rec.get("revenue_yoy")}% | 归母同比 {rec.get("netprofit_yoy")}%')
    time.sleep(0.5)
    ti += 1
    if ti >= 7:
        break
OUT['financials'] = fin_out

# ---------- 输出 ----------
os.makedirs('data', exist_ok=True)
with open('data/tushare_20260918.json', 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
print('\n[OK] 已保存 data/tushare_20260918.json')
print(f'[summary] 指数 {len(idx_out)} | 个股 {len(stk_out)} | 估值 {len(val_out)} | '
      f'资金 {len(mf_out)} | 财报 {len(fin_out)}')
