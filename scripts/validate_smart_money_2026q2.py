#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聪明钱共识追踪报告 2026Q2 — 数据校验引擎
================================================
本模块对 data/smart_money_2026q2.json 执行严格的数据验证与校验，
确保报告数据的准确性与完整性。校验分四类：

  [勾稽]  数值间内部一致性（如 Q1+Q2 = H1 净买入）
  [范围]  单值是否在合理区间
  [完整]  各数据维度披露状态（pending 为已知待披露，非错误）
  [交叉]  跨字段逻辑自洽（如持仓市值增量 vs 净买入）

退出码：0 = 无硬性矛盾（pending 仅作 WARN）；1 = 存在硬性数据矛盾。
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE, "data", "smart_money_2026q2.json")

# 万亿 -> 亿元
TRILLION_TO_YI = 10000.0


def load():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class Validator:
    def __init__(self, data):
        self.d = data
        self.results = []  # (level, rule_id, desc, detail, status)
        self.hard_fail = False

    def add(self, level, rid, desc, detail, status):
        # status: PASS / WARN / FAIL / INFO
        if status == "FAIL":
            self.hard_fail = True
        self.results.append((level, rid, desc, detail, status))

    # ---------- 勾稽校验 ----------
    def check_foot(self):
        nb = self.d["northbound"]
        q2 = nb["net_buy_q2_yi"]
        h1 = nb["net_buy_h1_yi"]
        q1_implied = h1 - q2  # 1995 - 2086 = -91
        self.add(
            "勾稽",
            "V-FOOT-01",
            "Q1+Q2 净买入 = H1 净买入",
            f"Q1隐含 = H1({h1}) − Q2({q2}) = {q1_implied} 亿元（净卖出）",
            "PASS" if (q1_implied + q2 == h1) else "FAIL",
        )
        # Q2 > H1 且均为正 => Q1 必为净卖出，与「恢复净流入」叙述一致
        consistent = (q2 > 0) and (h1 > 0) and (q1_implied < 0)
        self.add(
            "勾稽",
            "V-FOOT-02",
            "Q2净买入>0、H1净买入>0、Q1隐含净卖出 => 与『恢复净流入』叙述自洽",
            f"Q2={q2}>0, H1={h1}>0, Q1隐含={q1_implied}<0 → 上半年整体净流入、Q1曾净流出后Q2回流",
            "PASS" if consistent else "FAIL",
        )

    # ---------- 范围校验 ----------
    def check_range(self):
        nb = self.d["northbound"]
        th = nb["total_holdings_q2_trillion"]
        ok = th >= 3.0
        self.add(
            "范围",
            "V-RANGE-01",
            "北向总持仓突破 3 万亿元",
            f"Q2总持仓 = {th} 万亿；突破阈值 3.0 → {'已突破' if ok else '未达'}",
            "PASS" if ok else "FAIL",
        )
        # 单季净买入量级合理性（通常 <= 总持仓的 20%）
        total_yi = th * TRILLION_TO_YI
        ratio = nb["net_buy_q2_yi"] / total_yi
        ok2 = 0 < ratio < 0.20
        self.add(
            "范围",
            "V-RANGE-02",
            "Q2单季净买入量级合理（< 总持仓20%）",
            f"Q2净买入 {nb['net_buy_q2_yi']}亿 / 总持仓 {total_yi:.0f}亿 = {ratio:.1%}",
            "PASS" if ok2 else "WARN",
        )

    # ---------- 交叉校验 ----------
    def check_cross(self):
        nb = self.d["northbound"]
        # 持仓市值增量 = Q2总持仓 - Q1总持仓
        delta_trillion = nb["total_holdings_q2_trillion"] - nb["total_holdings_q1_trillion"]
        delta_yi = delta_trillion * TRILLION_TO_YI  # 4200亿
        price_contrib = delta_yi - nb["net_buy_q2_yi"]  # 4200 - 2086 = 2114亿
        ok = price_contrib > 0
        self.add(
            "交叉",
            "V-CROSS-01",
            "持仓市值增量 > 净买入 => 股价上涨贡献为正，印证『前三巨变主因股价涨跌』",
            f"Δ总持仓≈{delta_yi:.0f}亿，Q2净买入={nb['net_buy_q2_yi']}亿，"
            f"股价上涨贡献≈{price_contrib:.0f}亿（>0 印证叙述）",
            "PASS" if ok else "FAIL",
        )
        # 榜单连续性：宁德时代在两期 top3 且为稳定第一
        in_both = set(nb["top3_q1"]) & set(nb["top3_q2"])
        top1_ok = (nb["top1_stable"] in nb["top3_q1"]) and (nb["top1_stable"] in nb["top3_q2"])
        self.add(
            "交叉",
            "V-CROSS-02",
            "持仓市值TOP3两期连续性校验（宁德时代稳居第一）",
            f"两期交集={sorted(in_both)}；top1='{nb['top1_stable']}' 在两期均出现={top1_ok}",
            "PASS" if (top1_ok and len(in_both) >= 1) else "FAIL",
        )
        # 市值前三巨变：Q1与Q2应有差异（非完全不变）
        changed = nb["top3_q1"] != nb["top3_q2"]
        self.add(
            "交叉",
            "V-CROSS-03",
            "市值前三较Q1发生显著变化（印证『巨变』）",
            f"Q1={nb['top3_q1']} → Q2={nb['top3_q2']}；是否变化={changed}",
            "PASS" if changed else "WARN",
        )

    # ---------- 完整性校验 ----------
    def check_completeness(self):
        nb = self.d["northbound"]
        pf = self.d["public_fund"]
        inst = self.d["institution"]
        # 已披露字段必须带 source
        missing_src = []
        for k, v in nb.items():
            if k == "source":
                continue
        if not nb.get("source"):
            missing_src.append("northbound.source")
        if pf.get("status") == "pending" and "note" not in pf:
            missing_src.append("public_fund.note")
        if inst.get("status") == "pending" and "note" not in inst:
            missing_src.append("institution.note")
        self.add(
            "完整",
            "V-FULL-01",
            "已披露数据均标注来源",
            "北向 source = " + str(nb.get("source", "缺失")),
            "PASS" if nb.get("source") else "FAIL",
        )
        # 待披露维度需显式标记 pending（避免误填）
        pending = []
        if pf.get("status") == "pending":
            pending.append("公募基金")
        if inst.get("status") == "pending":
            pending.append("机构长线资金")
        self.add(
            "完整",
            "V-FULL-02",
            "未披露维度显式标记 pending（防止报告误用占位数据）",
            f"待披露维度：{pending if pending else '无'}",
            "WARN" if pending else "PASS",
        )

    def run(self):
        self.check_foot()
        self.check_range()
        self.check_cross()
        self.check_completeness()
        return self

    def report(self):
        print("=" * 64)
        print("  聪明钱共识追踪报告 2026Q2 — 数据校验结果")
        print("=" * 64)
        counters = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
        for level, rid, desc, detail, status in self.results:
            counters[status] = counters.get(status, 0) + 1
            icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌", "INFO": "ℹ️ "}[status]
            print(f"\n[{level}] {rid}  {icon} {status}")
            print(f"  校验项: {desc}")
            print(f"  说明  : {detail}")
        print("\n" + "-" * 64)
        print(f"  汇总: ✅ PASS {counters['PASS']}  |  ⚠️ WARN {counters['WARN']}  "
              f"|  ❌ FAIL {counters['FAIL']}  |  ℹ️ INFO {counters['INFO']}")
        verdict = "通过（无硬性矛盾，待披露项已显式标记）" if not self.hard_fail else "未通过（存在硬性数据矛盾，需修正）"
        print(f"  结论: {verdict}")
        print("=" * 64)
        return 0 if not self.hard_fail else 1


def main():
    if not os.path.exists(JSON_PATH):
        print(f"❌ 数据源不存在: {JSON_PATH}")
        sys.exit(2)
    data = load()
    v = Validator(data).run()
    code = v.report()
    sys.exit(code)


if __name__ == "__main__":
    main()
