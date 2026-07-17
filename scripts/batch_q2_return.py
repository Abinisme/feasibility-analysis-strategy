#!/usr/bin/env python3
"""NeoData 批量查询 Q2 前复权区间涨跌幅。
读取环境变量 NEODATA_TOKEN，对给定 (名称,代码) 列表逐一查询，
将原始响应存到 /tmp/nd_<code>.json，并提取含"区间涨跌幅"/"涨跌幅"的文本片段打印摘要。
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

URL = "https://copilot.tencent.com/agenttool/v1/neodata"

STOCKS = [
    ("宁德时代", "300750.SZ"),
    ("中际旭创", "300308.SZ"),
    ("北方华创", "002371.SZ"),
    ("美的集团", "000333.SZ"),
    ("贵州茅台", "600519.SH"),
    ("中微公司", "688012.SH"),
    ("新易盛", "300502.SZ"),
    ("澜起科技", "688008.SH"),
    ("立讯精密", "002475.SZ"),
    ("招商银行", "600036.SH"),
    ("天孚通信", "300394.SZ"),
    ("源杰科技", "688498.SH"),
]


def call_neodata(query_text):
    token = os.environ.get("NEODATA_TOKEN")
    if not token:
        raise RuntimeError("NEODATA_TOKEN 未设置")
    payload = {
        "query": query_text,
        "channel": "neodata",
        "sub_channel": "workbuddy",
        "data_type": "api",
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_text(resp):
    """从 apiData / docData 中抽取所有文本片段，方便定位涨跌幅。"""
    parts = []
    data = resp.get("data") or {}
    api = data.get("apiData") or {}
    for blk in api.get("apiRecall") or []:
        c = blk.get("content")
        if c:
            parts.append(c)
        d = blk.get("desc")
        if d:
            parts.append(d)
    doc = data.get("docData") or {}
    for grp in doc.get("docRecall") or []:
        for doc_item in grp.get("docList") or []:
            parts.append(doc_item.get("content") or doc_item.get("summary") or "")
    return "\n".join(str(p) for p in parts)


def main():
    if not os.environ.get("NEODATA_TOKEN"):
        print("ERROR: NEODATA_TOKEN 未设置")
        sys.exit(1)
    for name, code in STOCKS:
        try:
            resp = call_neodata(f"{name}{code} 2026年第二季度4月1日至6月30日的前复权区间涨跌幅")
            with open(f"/tmp/nd_{code}.json", "w") as f:
                json.dump(resp, f, ensure_ascii=False, indent=2)
            text = extract_text(resp)
            print(f"\n===== {name} {code} =====")
            # 打印含 涨跌幅 / 区间 / % 的行
            for line in text.splitlines():
                if any(k in line for k in ["涨跌幅", "区间", "%", "涨跌", "幅度", "收盘", "2026"]):
                    print(line[:300])
        except Exception as e:
            print(f"\n===== {name} {code} ===== ERROR: {e}")
        time.sleep(1)


if __name__ == "__main__":
    main()
