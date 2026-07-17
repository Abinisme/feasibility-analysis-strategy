#!/usr/bin/env python3
"""Tushare 前复权日线全量复核 Q2 区间涨跌幅，与 HTML 当前展示值对比。
Tushare daily 默认前复权，限频 1次/分钟，故每次调用 sleep 62s。
"""
import time
import tushare as ts

pro = ts.pro_api('09b30bfc56d9d23bd624fe8373df8490c37e848aa749da28154c9543')

# (名称, 代码, HTML当前展示的Q2涨跌幅%)
EXPECT = [
    ("宁德时代", "300750.SZ", -0.5),
    ("中际旭创", "300308.SZ", 123.4),
    ("北方华创", "002371.SZ", 98.1),
    ("美的集团", "000333.SZ", 4.0),
    ("贵州茅台", "600519.SH", -16.6),
    ("中微公司", "688012.SH", 52.9),
    ("新易盛", "300502.SZ", 37.1),
    ("澜起科技", "688008.SH", 147.4),
    ("立讯精密", "002475.SZ", 42.9),
    ("招商银行", "600036.SH", -9.7),
    ("恒立液压", "601100.SH", 12.0),
    ("特锐德", "300001.SZ", 39.1),
    ("思源电气", "002028.SZ", -14.4),
    ("紫金矿业", "601899.SH", -23.2),
    ("汇川技术", "300124.SZ", -1.0),
    ("中国平安", "601318.SH", -15.9),
    ("天孚通信", "300394.SZ", None),
    ("源杰科技", "688498.SH", None),
]


def q2_return(code):
    df = pro.daily(ts_code=code, start_date="20260331", end_date="20260630",
                  fields="trade_date,close")
    if df is None or df.empty:
        return None, None, None
    df = df.sort_values("trade_date")
    c_start = float(df.iloc[0]["close"])   # 03-31
    c_end = float(df.iloc[-1]["close"])    # 06-30
    return c_start, c_end, (c_end / c_start - 1) * 100


print(f"{'名称':<8}{'代码':<10}{'03-31收':>10}{'06-30收':>10}{'Tushare%':>10}{'HTML%':>9}  差异")
print("-" * 70)
for name, code, html_val in EXPECT:
    try:
        time.sleep(62)
        c0, c1, ret = q2_return(code)
        if ret is None:
            print(f"{name:<8}{code:<10}  NO DATA")
            continue
        diff = "" if html_val is None else f"{(ret-html_val):+.1f}"
        html_s = "  -  " if html_val is None else f"{html_val:>7.1f}"
        print(f"{name:<8}{code:<10}{c0:>10.2f}{c1:>10.2f}{ret:>9.1f}%{html_s:>9}  {diff}")
    except Exception as e:
        print(f"{name:<8}{code:<10}  ERR {e}")
print("=== DONE ===")
