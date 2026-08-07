#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成首页「复盘合集」HTML 片段：本站A股复盘 + 任务库复盘，按日期倒序分组"""
import re, os, html, datetime
from collections import OrderedDict

BASE = "/Users/yntwt/feasibility-analysis-strategy"
TASK_DIR = os.path.join(BASE, "复盘合集")

def parse_date(name):
    """从文件名解析日期，返回 (date, label)"""
    # 本站格式: A股深度复盘_20260716.md
    m = re.search(r"A股深度复盘[_](\d{8})", name)
    if m:
        d = m.group(1)
        return datetime.date(int(d[:4]), int(d[4:6]), int(d[6:8])), name
    # 任务库格式1: 持仓复盘_20260324.md / 持仓回撤复盘_20260403.md
    m = re.search(r"持仓.*?_(\d{4})(\d{2})(\d{2})", name)
    if m:
        y, mo, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo <= 12 and dd <= 31:
            return datetime.date(y, mo, dd), name
    m = re.search(r"持仓复盘_(\d{4})(\d{2})(\d{2})_(\d{4})", name)
    if m:
        y, mo, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return datetime.date(y, mo, dd), name
    # 任务库格式2: 2026-04-10_持仓复盘.md / 2026-05-13复盘.md
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", name)
    if m:
        y, mo, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo <= 12 and dd <= 31:
            return datetime.date(y, mo, dd), name
    # 任务库格式3: 复盘报告-2026年5月19日.md
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", name)
    if m:
        y, mo, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo <= 12 and dd <= 31:
            return datetime.date(y, mo, dd), name
    # 任务库格式4: 复盘报告-2026-05-14.md
    m = re.search(r"复盘报告-(\d{4})-(\d{2})-(\d{2})", name)
    if m:
        y, mo, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return datetime.date(y, mo, dd), name
    return None, name

def title_of(name, src):
    """生成可读标题"""
    base = re.sub(r"\.md$", "", name)
    t = base
    if src == "本站A股复盘":
        # A股深度复盘_20260716 -> 深度复盘
        t = re.sub(r"A股深度复盘_\d{8}", "A股深度复盘", base)
        return t
    # 任务库
    # 处理持仓复盘类
    if t.startswith("持仓复盘_"):
        # 持仓复盘_20260324 -> 持仓复盘
        t = re.sub(r"_?\d{8}(_\d{4})?$", "", t)
        return t
    if t.startswith("持仓回撤复盘_"):
        t = "持仓回撤复盘"
        return t
    if t.startswith("2026-") or re.match(r"^\d{4}-\d{2}-\d{2}", t):
        # 2026-04-10_持仓复盘 / 2026-05-13复盘 / 2026-05-13 持仓复盘
        t = re.sub(r"^\d{4}-\d{2}-\d{2}[ _]?", "", t)
        return t or "复盘"
    if t.startswith("复盘报告-2026年"):
        t = re.sub(r"^复盘报告-2026年\d{1,2}月\d{1,2}日", "复盘报告", t)
        return t or "复盘报告"
    if t.startswith("复盘报告-2026-"):
        t = re.sub(r"^复盘报告-2026-\d{2}-\d{2}", "复盘报告", t)
        return t or "复盘报告"
    return t

# 收集文件
items = []
for f in sorted(os.listdir(BASE)):
    if f.startswith("A股深度复盘_") and f.endswith(".md"):
        d, _ = parse_date(f)
        if d:
            items.append((d, f, "./" + f, "本站A股复盘"))
for f in sorted(os.listdir(TASK_DIR)):
    if not f.endswith(".md"):
        continue
    d, _ = parse_date(f)
    if d:
        items.append((d, f, "./复盘合集/" + f, "任务库持仓复盘"))

# 按日期倒序
items.sort(key=lambda x: x[0], reverse=True)

# 按月份分组
groups = OrderedDict()
for d, f, link, src in items:
    key = f"{d.year}年{d.month:02d}月"
    groups.setdefault(key, []).append((d, f, link, src))

total = len(items)
out = []
out.append('''            <!-- ===== 复盘合集 ===== -->
            <div class="replay-section">
                <div class="replay-header">
                    <h2>📚 复盘合集</h2>
                    <span class="replay-count">共 %d 篇</span>
                </div>
                <p class="replay-desc">A股每日深度复盘（本站）+ 持仓复盘（任务库），按日期倒序排列，7/16 两篇并存。</p>''' % total)

for key, sub in groups.items():
    open_attr = ' open' if key.startswith("2026年08") else ''
    out.append(f'''                <details class="replay-month"{open_attr}>
                    <summary>{key} · {len(sub)} 篇</summary>
                    <ul class="replay-list">''')
    for d, f, link, src in sub:
        t = title_of(f, src)
        date_str = f"{d.month}/{d.day}"
        tag_cls = "tag-a" if src == "本站A股复盘" else "tag-b"
        out.append(f'''                        <li><a href="{link}"><span class="replay-date">{date_str}</span><span class="replay-title">{html.escape(t)}</span><span class="replay-src {tag_cls}">{src}</span></a></li>''')
    out.append('''                </details>''')

out.append('''            </div>''')
print("\n".join(out))
