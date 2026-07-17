#!/usr/bin/env python3
"""NeoData 金融搜索查询脚本（腾讯金融数据源）。
依赖环境变量 NEODATA_TOKEN（JWT），由 connect_cloud_service 获取后 export。
用法: python scripts/query.py --query "查询内容" [--data-type api|doc|all]
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error

URL = "https://copilot.tencent.com/agenttool/v1/neodata"


def query(query_text, data_type="all"):
    token = os.environ.get("NEODATA_TOKEN")
    if not token:
        raise RuntimeError("NEODATA_TOKEN 未设置，请先 connect_cloud_service 并 export")
    payload = {
        "query": query_text,
        "channel": "neodata",
        "sub_channel": "workbuddy",
        "data_type": data_type,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"code": str(e.code), "msg": e.reason, "raw": e.read().decode("utf-8", "ignore")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--data-type", default="all")
    args = ap.parse_args()
    out = query(args.query, args.data_type)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
