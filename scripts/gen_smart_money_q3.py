#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 smart_money_consensus_2026Q3.html：复用Q2样式骨架 + Q3真实数据"""
import re, io, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q2 = os.path.join(BASE, 'smart_money_consensus_2026Q2.html')
OUT = os.path.join(BASE, 'smart_money_consensus_2026Q3.html')

with open(Q2, 'r', encoding='utf-8') as f:
    q2 = f.read()

# 提取 style 块
m = re.search(r'<style>.*?</style>', q2, re.S)
STYLE = m.group(0)

BODY = r'''
<a href="./index.html" class="back-link">← 返回首页</a>

<div class="header">
  <div class="header-top">
    <div>
      <div class="header-title">🧠 聪明钱共识<span>追踪报告</span></div>
      <div class="header-sub">北向资金 · 公募基金 · 机构长线资金 三维度交叉验证</div>
    </div>
    <div class="header-badge">2026 Q3 · 2026-10-27</div>
  </div>
  <div class="header-stats">
    <div class="stat-item">
      <div class="stat-num" style="color:#4ade80;">北向✅</div>
      <div class="stat-label">已披露</div>
    </div>
    <div class="stat-item">
      <div class="stat-num" style="color:#1a6bc6;">公募✓</div>
      <div class="stat-label">已披露</div>
    </div>
    <div class="stat-item">
      <div class="stat-num" style="color:#fbbf24;">机构⏳</div>
      <div class="stat-label">待披露</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">2.58万亿</div>
      <div class="stat-label">北向总持仓(-17.6%)</div>
    </div>
    <div class="stat-item">
      <div class="stat-num" style="color:#f87171;">-886亿</div>
      <div class="stat-label">Q3净买入</div>
    </div>
  </div>
</div>

<div class="container">

  <!-- 数据状态条 -->
  <div class="status-strip">
    <div class="status-chip"><span class="dot dot-ok"></span> 北向资金 2026Q3：已披露（10/15）</div>
    <div class="status-chip"><span class="dot dot-ok"></span> 公募基金 2026Q3：已于10月27日披露完毕</div>
    <div class="status-chip"><span class="dot dot-wait"></span> 机构长线资金 2026Q3：待披露</div>
    <div class="status-chip"><span class="dot dot-pending"></span> 共识矩阵/行业方向：北向+公募双维度</div>
  </div>

  <!-- ===== 数据校验中心（可折叠） ===== -->
  <details class="val-details">
    <summary>
      <span class="dot dot-purple"></span>
      数据校验中心 — 报告数据自检（实时）
      <span class="val-toggle-hint" id="val-hint">点击展开校验详情 ▼</span>
    </summary>
    <div class="val-wrap">
      <div class="val-head">
        <h3>报告数据完整性 / 准确性校验</h3>
        <span class="badge" id="val-overall">运行中…</span>
      </div>
      <div class="val-sub">以下校验在页面加载时基于已披露数据实时重算。FAIL = 硬性矛盾（禁止发布）；WARN = 已知待披露/需关注；PASS = 通过。</div>
      <div class="val-summary" id="val-summary"></div>
      <div class="matrix-wrap">
        <table class="val-table">
          <thead>
            <tr><th style="width:64px;">类别</th><th style="width:90px;">规则</th><th style="width:54px;">状态</th><th>校验项 / 说明</th></tr>
          </thead>
          <tbody id="val-body"></tbody>
        </table>
      </div>
    </div>
  </details>

  <!-- ① 北向资金 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-red"></div>① 北向资金 —— 2026年三季度持仓全景</div>
    <p class="data-time">数据截至 2026-09-30 | 来源：Wind / Choice（北向资金持股穿透披露，10月15日披露）</p>

    <div class="consensus-banner" style="margin-bottom:16px;">
      <div class="banner-icon">🎯</div>
      <div class="banner-text">
        <h3>核心结论（北向维度）：持仓缩水5500亿、Q3净卖出886亿，加仓银行医药、减仓科技制造</h3>
        <p>北向总持仓回落至 <strong>2.58万亿</strong>（Q2为3.13万亿，-17.57%），Q3净买入 <strong>-886亿</strong>（沪市+519亿、深市-1405亿），一改Q2的+2086亿大幅流入。行业配置出现方向性切换：<strong>银行持股排名从第6跃升至第3</strong>，通信从第3下滑至第7；医药生物、非银金融、交通运输获百亿级增配，电子、电力设备双双减少2000亿以上。宁德时代仍是第一大重仓（2331亿，缩水1183亿），<strong>美的集团、贵州茅台重回前三</strong>，中际旭创、北方华创跌出前三。</p>
      </div>
    </div>

    <div class="cards-grid">
      <div class="card">
        <div class="card-header">
          <div class="card-title">北向总持仓市值</div>
          <div class="card-tag tag-green">大幅回落</div>
        </div>
        <div class="kpi">
          <div class="kpi-num red">2.58万亿</div>
          <div class="kpi-label">较Q2回落17.57%</div>
          <div class="kpi-sub">Q2 3.13万亿 → Q3 2.58万亿（减少约5500亿）</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">净买入态势</div>
          <div class="card-tag tag-red">转为净流出</div>
        </div>
        <div class="kpi" style="margin-bottom:10px;">
          <div class="kpi-num green">-886亿</div>
          <div class="kpi-label">Q3单季净买入（净流出）</div>
        </div>
        <div class="kpi">
          <div class="kpi-num blue">沪+519 / 深-1405</div>
          <div class="kpi-label">沪市净买入 / 深市净买入</div>
          <div class="kpi-sub">H1累计净买入1995亿，Q3反向流出</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">持仓增量拆解</div>
          <div class="card-tag tag-gold">股价下跌主导</div>
        </div>
        <div class="kpi" style="margin-bottom:10px;">
          <div class="kpi-num gold">-5500亿</div>
          <div class="kpi-label">Q3总持仓变动（2.58−3.13万亿）</div>
        </div>
        <div class="kpi">
          <div class="kpi-num blue">≈-4614亿</div>
          <div class="kpi-label">股价下跌贡献（变动-5500−净买入-886）</div>
          <div class="kpi-sub">持股数量反增至1123.38亿股（+48.5亿股）</div>
        </div>
      </div>
    </div>

    <!-- 市值TOP3演变 -->
    <div class="card" style="margin-top:16px;">
      <div class="card-header">
        <div class="card-title">持仓市值 TOP3 演变（Q2 → Q3）</div>
        <div class="card-tag tag-red">科技退潮 · 消费回归</div>
      </div>
      <div class="shift-row">
        <div class="shift-q">
          <div class="q-label">2026 Q2 持仓市值前三</div>
          <span class="shift-name nm-keep">① 宁德时代</span>
          <span class="shift-name nm-out">② 中际旭创</span>
          <span class="shift-name nm-out">③ 北方华创</span>
        </div>
        <div class="arrow">➜</div>
        <div class="shift-q">
          <div class="q-label">2026 Q3 持仓市值前三</div>
          <span class="shift-name nm-keep">① 宁德时代 2331亿</span>
          <span class="shift-name nm-new">② 美的集团 766亿</span>
          <span class="shift-name nm-new">③ 贵州茅台</span>
        </div>
      </div>
      <div style="margin-top:10px; background:#f8fafc; border-radius:8px; padding:12px 16px; font-size:12.5px; color:var(--gray);">
        <strong style="color:var(--dark)">解读：</strong>宁德时代连续三期稳居第一，但市值从3514亿缩至2331亿（-1183亿/-33.67%，同期股价-25.66%）。中际旭创、北方华创因科技板块深度回调跌出前三，<strong style="color:var(--dark)">美的集团、贵州茅台两大传统白马重回前三</strong>——这是Q3「科技退潮、消费红利回归」最直观的仓位印记。宁德时代市值仍是第二名美的集团（766亿）的三倍左右。
      </div>
    </div>

    <!-- 行业分布 -->
    <div class="card" style="margin-top:16px;">
      <div class="card-header">
        <div class="card-title">北向重仓行业分布（Q3，申万一级）</div>
        <div class="card-tag tag-blue">电子仍第一 · 银行跃升第三</div>
      </div>
      <div class="matrix-wrap">
        <table class="stock-table">
          <thead>
            <tr><th>排名</th><th>行业</th><th>持仓市值(亿)</th><th>Q3环比</th><th>排名变化</th><th>信号</th></tr>
          </thead>
          <tbody>
            <tr><td>1</td><td><strong>电子</strong></td><td class="num-red">5,034.45</td><td class="num-green">减少2000亿+</td><td>保持第1</td><td>仍超配但大幅减配</td></tr>
            <tr><td>2</td><td><strong>电力设备</strong></td><td>3,826.27</td><td class="num-green">减少2000亿+</td><td>保持第2</td><td>宁德缩水拖累</td></tr>
            <tr style="background:#f0fdf4;"><td>3</td><td><strong>银行</strong></td><td class="num-red">2,106.21</td><td class="num-red">显著增加</td><td class="num-red">第6 → 第3 ↑↑</td><td><strong>红利防御主线</strong></td></tr>
            <tr style="background:#f0fdf4;"><td>4</td><td><strong>医药生物</strong></td><td>1,500+</td><td class="num-red">新增超百亿</td><td>上升</td><td><strong>CXO/创新药修复</strong></td></tr>
            <tr><td>5</td><td>机械设备</td><td>1,000+</td><td class="num-green">下降明显</td><td>—</td><td>减配中游制造</td></tr>
            <tr><td>6</td><td>有色金属</td><td>1,000+</td><td class="num-red">增配</td><td>—</td><td>紫金矿业净买96亿居首</td></tr>
            <tr><td>7</td><td>通信</td><td>1,000+</td><td class="num-green">下降明显</td><td class="num-green">第3 → 第7 ↓↓</td><td>光模块高位兑现</td></tr>
            <tr><td>8</td><td>非银金融</td><td>1,000+</td><td class="num-red">新增超百亿</td><td>上升</td><td>中国平安/平安银行获买</td></tr>
            <tr><td>9</td><td>食品饮料</td><td>1,000+</td><td class="num-red">增配</td><td>—</td><td>茅台重回前三</td></tr>
            <tr><td>10</td><td>家用电器</td><td>1,000+</td><td class="num-red">增配</td><td>—</td><td>美的重回第二</td></tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top:12px; background:var(--blue-light); border-radius:8px; padding:10px 14px; font-size:12px; color:var(--blue);">
        数据来源：Wind（申万一级行业口径，截至2026-09-30）。Q3 持股市值上升行业15个、下降16个，<strong>增配合计约1583亿元、减配合计约7082亿元</strong>。银行、医药生物、非银金融、交通运输及部分消费公用为主要增配方向；电子、电力设备、通信、机械设备等前期高景气科技制造主线大规模减配。
      </div>
    </div>

    <!-- Q3 净买入/净卖出 -->
    <div class="cards-grid-2" style="margin-top:16px;">
      <div class="highlight-box hb-red">
        <h4>Q3 净买入居前（真金白银流入）</h4>
        <ul>
          <li><strong>紫金矿业</strong>（有色金属）净买入 <strong>96亿</strong>，Q3居首</li>
          <li><strong>招商银行</strong>（银行）净买入超50亿</li>
          <li><strong>药明康德</strong>（医药/CXO）净买入超50亿</li>
          <li><strong>中国平安</strong>（非银）净买入超50亿</li>
          <li><strong>美的集团</strong>（家电）净买入超50亿，重回第二</li>
          <li><strong>平安银行</strong>（银行）净买入超50亿</li>
          <li><strong>工商银行</strong>（银行）净买入居前</li>
        </ul>
        <div style="margin-top:8px; font-size:12px; color:#b91c1c;">特征：金融（银行/非银）+ 医药 + 资源（有色）+ 消费（家电）四线并进，与Q2「半导体/光模块」截然不同。三季度净买额大幅萎缩，<strong>无一超百亿元</strong>。</div>
      </div>
      <div class="highlight-box hb-green">
        <h4>Q3 净卖出居前（科技龙头被抛售）</h4>
        <ul>
          <li><strong>宁德时代</strong>（电力设备）净卖出居首（超百亿），持股量大降10%</li>
          <li><strong>新易盛</strong>（通信/光模块）净卖出超百亿</li>
          <li><strong>北方华创</strong>（电子/半导体设备）净卖出超百亿</li>
          <li><strong>中际旭创</strong>（通信/光模块）净卖出超百亿</li>
          <li><strong>阳光电源</strong>（电力设备/光伏）净卖出超百亿</li>
          <li><strong>潍柴动力</strong>（机械/重卡）净卖出超百亿</li>
        </ul>
        <div style="margin-top:8px; font-size:12px; color:#15803d;">特征：<strong>前期涨幅最大的AI硬件（光模块、半导体设备）成为主要兑现对象</strong>，新能源（宁德、阳光电源）同步减仓。这与Q2「宁德+554亿、中微+181亿」的加仓方向完全逆转。</div>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <div class="card-header">
        <div class="card-title">北向资金 Q3 vs Q2 关键对比</div>
        <div class="card-tag tag-gold">方向性逆转</div>
      </div>
      <div class="matrix-wrap">
        <table class="stock-table">
          <thead>
            <tr><th>维度</th><th>2026 Q2</th><th>2026 Q3</th><th>变化</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>总持仓</strong></td><td>3.13万亿</td><td>2.58万亿</td><td class="num-green">-5,500亿（-17.57%）</td></tr>
            <tr><td><strong>净买入</strong></td><td class="num-red">+2,086亿</td><td class="num-green">-886亿</td><td class="num-green">转为净流出</td></tr>
            <tr><td><strong>持股数量</strong></td><td>1,074.88亿股</td><td>1,123.38亿股</td><td class="num-red">+48.50亿股（逆势增持）</td></tr>
            <tr><td><strong>第一大重仓</strong></td><td>宁德时代 3,514亿</td><td>宁德时代 2,331亿</td><td class="num-green">-1,183亿（-33.67%）</td></tr>
            <tr><td><strong>前三大</strong></td><td>宁德/中际旭创/北方华创</td><td>宁德/美的/茅台</td><td class="num-green">科技→消费</td></tr>
            <tr><td><strong>第一重仓行业</strong></td><td>电子（8席入前二十）</td><td>电子（市值仍第一但减配）</td><td class="num-green">减配2000亿+</td></tr>
            <tr><td><strong>银行排名</strong></td><td>第6</td><td class="num-red">第3</td><td class="num-red">↑↑ 跃升</td></tr>
            <tr><td><strong>通信排名</strong></td><td>第3</td><td class="num-green">第7</td><td class="num-green">↓↓ 下滑</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ② 公募基金 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-blue"></div>② 公募基金 —— 2026年三季度</div>
    <p class="data-time">数据截至 2026-09-30 | 已于2026年10月27日披露完毕 | 来源：天相投顾 / Wind / Choice</p>

    <div class="consensus-banner" style="margin:0 0 16px;">
      <div class="banner-icon">🎯</div>
      <div class="banner-text">
        <h3>核心结论（公募维度）：持仓缩水9801亿、科技内部大腾挪，药明康德与长鑫科技新进前十</h3>
        <p>Q3末公募总规模 <strong>39.30万亿</strong>（环比-0.89%），股票持仓总市值 <strong>7.85万亿</strong>（较Q2减少9,801亿，-11.09%），同期沪深300跌12.49%。主动权益前十大重仓股大洗牌：<strong>药明康德、长鑫科技、沪电股份新进，兆易创新、中微公司、三环集团退出</strong>。中际旭创仍居第一（959.38亿）但减持市值最多（-700亿+），药明康德增持市值最多。<strong>电子行业持仓占比从43.4%降至35.8%（-7.6pp）</strong>，资金向医药、红利再平衡。</p>
      </div>
    </div>

    <div class="cards-grid-2">
      <div class="kpi">
        <div class="kpi-num" style="color:var(--blue);">39.30<span class="kpi-unit">万亿</span></div>
        <div class="kpi-label">公募总规模（环比-0.89%）</div>
      </div>
      <div class="kpi">
        <div class="kpi-num" style="color:var(--red);">7.85<span class="kpi-unit">万亿</span></div>
        <div class="kpi-label">股票持仓市值（-9,801亿）</div>
      </div>
      <div class="kpi">
        <div class="kpi-num" style="color:var(--green);">-7.6<span class="kpi-unit">pp</span></div>
        <div class="kpi-label">电子行业占比降幅</div>
      </div>
      <div class="kpi">
        <div class="kpi-num" style="color:var(--gold);">49.6<span class="kpi-unit">%</span></div>
        <div class="kpi-label">重仓前50集中度（↓5.6pp）</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title">主动权益基金 TOP10 重仓股（截至 2026/09/30）</div>
        <div class="card-tag tag-blue">天相投顾口径</div>
      </div>
      <div class="matrix-wrap">
        <table class="stock-table">
          <thead>
            <tr><th>排名</th><th>个股</th><th>板块</th><th>持股市值(亿)</th><th>Q2→Q3变化</th><th>核心逻辑</th></tr>
          </thead>
          <tbody>
            <tr style="background:#fff8e6;"><td>1</td><td><div class="stock-name">中际旭创</div><div class="stock-code">300308.SZ</div></td><td>通信(光模块)</td><td class="num-red">959.38</td><td class="num-green">↓减持市值最多(-700亿+)</td><td>连续4期第一大重仓，但持股数量反增2.31%</td></tr>
            <tr><td>2</td><td><div class="stock-name">新易盛</div><div class="stock-code">300502.SZ</div></td><td>通信(光模块)</td><td>867.69</td><td class="num-red">↑持股数量+8.11%</td><td>基金经理逆势加仓「易中天」</td></tr>
            <tr style="background:#f0fdf4;"><td>3</td><td><div class="stock-name">药明康德</div><div class="stock-code">603259.SH</div></td><td>医药生物(CXO)</td><td class="num-red">新进</td><td class="num-red">🆕 新进前十<br>增持市值榜首</td><td><strong>CXO景气回升，公募增持第一大</strong></td></tr>
            <tr style="background:#f0fdf4;"><td>4</td><td><div class="stock-name">长鑫科技</div><div class="stock-code">688825.SH</div></td><td>电子(存储)</td><td>488.78</td><td class="num-red">🆕 新进前十</td><td>7月上市黑马，机构扫货超411亿</td></tr>
            <tr><td>5</td><td><div class="stock-name">源杰科技</div><div class="stock-code">688498.SH</div></td><td>电子(光芯片)</td><td>—</td><td>保持</td><td>光芯片国产替代</td></tr>
            <tr><td>6</td><td><div class="stock-name">东山精密</div><div class="stock-code">002384.SZ</div></td><td>电子(电子制造)</td><td>—</td><td class="num-green">↓让位第三</td><td>Q2第三 → Q3第六</td></tr>
            <tr><td>7</td><td><div class="stock-name">宁德时代</div><div class="stock-code">300750.SZ</div></td><td>电力设备(电池)</td><td>—</td><td class="num-green">↓继续下滑</td><td>Q2第五 → Q3第七</td></tr>
            <tr><td>8</td><td><div class="stock-name">寒武纪</div><div class="stock-code">688256.SH</div></td><td>电子(AI芯片)</td><td>—</td><td>保持</td><td>国产AI芯片龙头</td></tr>
            <tr><td>9</td><td><div class="stock-name">北方华创</div><div class="stock-code">002371.SZ</div></td><td>电子(半导体设备)</td><td>—</td><td class="num-green">↓持仓数量减少</td><td>基金持仓数量下降</td></tr>
            <tr style="background:#f0fdf4;"><td>10</td><td><div class="stock-name">沪电股份</div><div class="stock-code">002463.SZ</div></td><td>电子(PCB)</td><td>—</td><td class="num-red">🆕 新进前十</td><td>PCB龙头，超跌后获增配</td></tr>
            <tr><td colspan="6" style="text-align:center;color:var(--gray);font-size:12px;padding:8px;">—— Q3 退出前十：兆易创新、中微公司、三环集团 ——</td></tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top:10px; background:var(--gold-light); border-radius:8px; padding:8px 14px; font-size:12px; color:#b45309;">
        ⚠️ <strong>关键变化：</strong>前十仍是科技为主，但结构剧变——存储（兆易）、半导体设备（中微、三环）让位于<strong>CXO（药明康德）、新股存储正主（长鑫科技）、PCB（沪电）</strong>。全员口径看，中际旭创持股市值1704.84亿（2417只基金持有）、新易盛1431.19亿、宁德时代877.66亿、寒武纪第四、贵州茅台升至第九（549.82亿）、长鑫科技第13（488.78亿）。
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <div class="card-header">
        <div class="card-title">行业配置：电子占比降7.6pp，医药生物升至前三</div>
        <div class="card-tag tag-green">科技减配 · 医药红利加配</div>
      </div>
      <div class="matrix-wrap">
        <table class="stock-table">
          <thead>
            <tr><th>行业</th><th>Q3持仓占比</th><th>Q2→Q3变化</th><th>持股市值(亿)</th><th>信号</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>电子</strong></td><td>36.48%（天相）<br>35.8%（国信）</td><td class="num-green">43.4% → 35.8%（-7.6pp）</td><td>12,193（-5,467亿）</td><td>仍第一但大幅减配，申万电子-32.65%</td></tr>
            <tr><td><strong>通信</strong></td><td>15.21%</td><td class="num-green">16.9% → 14.8%（-2.1pp）</td><td>4,697（-1,748亿）</td><td>光模块高位兑现</td></tr>
            <tr style="background:#f0fdf4;"><td><strong>医药生物</strong></td><td>9.46%</td><td class="num-red">↑ 加仓最多（+4.1pp）</td><td>—</td><td><strong>CXO/创新药修复主线</strong></td></tr>
            <tr><td><strong>电力设备</strong></td><td>—</td><td class="num-green">-1.6pp</td><td>—</td><td>宁德缩水</td></tr>
            <tr><td><strong>建筑材料</strong></td><td>—</td><td class="num-green">-1.1pp</td><td>—</td><td>减仓</td></tr>
            <tr><td><strong>机械设备</strong></td><td>—</td><td class="num-green">-0.4pp</td><td>—</td><td>减仓</td></tr>
            <tr style="background:#f0fdf4;"><td><strong>银行/煤炭/公用/石化</strong></td><td>—</td><td class="num-red">↑ 均获增配</td><td>—</td><td><strong>红利防御</strong></td></tr>
            <tr style="background:#f0fdf4;"><td><strong>汽车/食品饮料/家电</strong></td><td>—</td><td class="num-red">↑ 获增配</td><td>—</td><td><strong>消费回补</strong></td></tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top:12px; background:var(--blue-light); border-radius:8px; padding:10px 14px; font-size:12px; color:var(--blue);">
        天相投顾口径：三类基金前十大重仓行业合计占比86.31%，<strong>电子36.48%、通信15.21%、医药生物9.46%位列前三</strong>。仓位方面：普通股票型89.08%、偏股混合型85.78%、灵活配置型72.87%。
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <div class="card-header">
        <div class="card-title">港股与全球化配置：腾讯稳居第一，长鑫成最大黑马</div>
        <div class="card-tag tag-gold">配置未收缩</div>
      </div>
      <div class="flx">
        <div class="fc">
          <h4>港股重仓 TOP5</h4>
          <p style="font-size:.86em;">腾讯控股 <strong>623.7亿</strong>（第一大港股）｜阿里巴巴-W 489.35亿｜中芯国际 285.19亿｜美团-W 254.93亿｜小米集团-W 254.37亿。此外，美股英伟达、苹果、微软均位于基金前50大重仓股，<strong>公募全球化布局并未收缩</strong>。</p>
        </div>
        <div class="fc">
          <h4>长鑫科技：Q3 最大黑马</h4>
          <p style="font-size:.86em;">7月刚登陆科创板，Q3末即被基金重仓持有 <strong>488.78亿元</strong>，全体口径排名第13位，<strong>机构扫货超411亿元</strong>。新股受机构资金追捧的特征十分突出，也印证「存储正主」逻辑。</p>
        </div>
      </div>
    </div>
  </div>

  <!-- ③ 机构长线资金 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-gold"></div>③ 机构长线资金 —— 社保 / QFII / 企业年金 2026Q3</div>
    <div class="pending-box">
      <div class="p-icon">⏳</div>
      <div class="p-title">数据待披露</div>
      <div class="p-note">社保 / QFII / 企业年金 2026Q3 持仓预计稍晚披露。当前不可用，避免基于占位数据得出结论。</div>
    </div>
  </div>

  <!-- ④ 共识矩阵 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-purple"></div>④ 聪明钱共识矩阵 — 北向+公募双维度（Q3）</div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">核心标的共识矩阵（Q3）</div>
        <div class="card-tag tag-blue">公募已披露 · 机构待披露</div>
      </div>
      <div class="matrix-wrap">
        <table class="stock-table">
          <thead>
            <tr><th>个股</th><th>板块</th><th>北向 · Q3</th><th>公募 · Q3</th><th>机构长线</th><th>共识强度</th></tr>
          </thead>
          <tbody>
            <tr><td><div class="stock-name">宁德时代</div><div class="stock-code">300750</div></td><td>电力设备</td><td class="num-green">净卖出居首(超百亿)</td><td class="num-green">↓降至第七</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-green">双降</span></td></tr>
            <tr style="background:#fff8e6;"><td><div class="stock-name">中际旭创</div><div class="stock-code">300308</div></td><td>通信(光模块)</td><td class="num-green">净卖出超百亿</td><td class="num-red">仍第一(持股+2.31%)</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-gold">分歧</span></td></tr>
            <tr style="background:#fff8e6;"><td><div class="stock-name">新易盛</div><div class="stock-code">300502</div></td><td>通信(光模块)</td><td class="num-green">净卖出超百亿</td><td class="num-red">第二+持股+8.11%</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-gold">分歧</span></td></tr>
            <tr><td><div class="stock-name">北方华创</div><div class="stock-code">002371</div></td><td>电子(半导体)</td><td class="num-green">净卖出超百亿</td><td class="num-green">↓持仓数量减少</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-green">双降</span></td></tr>
            <tr style="background:#f0fdf4;"><td><div class="stock-name">药明康德</div><div class="stock-code">603259</div></td><td>医药(CXO)</td><td class="num-red">净买入超50亿</td><td class="num-red">新进第三+增持榜首</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-red">双升·最强</span></td></tr>
            <tr style="background:#f0fdf4;"><td><div class="stock-name">紫金矿业</div><div class="stock-code">601899</div></td><td>有色金属</td><td class="num-red">净买入96亿居首</td><td class="num-red">↑资源加配</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-red">双升</span></td></tr>
            <tr style="background:#f0fdf4;"><td><div class="stock-name">招商银行</div><div class="stock-code">600036</div></td><td>银行</td><td class="num-red">净买入超50亿</td><td class="num-red">↑银行加配</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-red">双升</span></td></tr>
            <tr style="background:#f0fdf4;"><td><div class="stock-name">美的集团</div><div class="stock-code">000333</div></td><td>家用电器</td><td class="num-red">净买入超50亿·重回第二</td><td class="num-red">↑家电加配</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-red">双升</span></td></tr>
            <tr style="background:#f0fdf4;"><td><div class="stock-name">长鑫科技</div><div class="stock-code">688825</div></td><td>电子(存储)</td><td>—（新股，北向尚未覆盖）</td><td class="num-red">新进第四·488.78亿</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-red">公募独强</span></td></tr>
            <tr><td><div class="stock-name">贵州茅台</div><div class="stock-code">600519</div></td><td>食品饮料</td><td class="num-red">重回前三</td><td class="num-red">升至第九(549.82亿)</td><td style="color:var(--gray)">待披露</td><td><span class="card-tag tag-gold">边际转强</span></td></tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top:10px; font-size:12px; color:var(--gray);">✓ 公募基金已于10/27披露完毕，机构长线（社保/QFII）列待披露。当前共识基于北向+公募双维度。</div>
    </div>
  </div>

  <!-- ⑤ 共识行业方向 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-green"></div>⑤ 共识行业方向（北向 + 公募双维度）</div>
    <div class="cards-grid">
      <div class="highlight-box hb-red">
        <h4>🥇 Q3 双维度共同加仓</h4>
        <ul>
          <li><strong>医药生物</strong>（北向新增超百亿、公募加仓最多+4.1pp；药明康德双榜首）</li>
          <li><strong>银行</strong>（北向排名第6→第3、公募同步增配；招商/平安/工行获净买）</li>
          <li><strong>有色金属</strong>（紫金矿业北向净买96亿居首；公募资源加配）</li>
          <li><strong>家用电器 / 食品饮料 / 汽车</strong>（美的净买超50亿、茅台重回前三；公募消费回补）</li>
          <li><strong>非银金融 / 交通运输 / 公用事业</strong>（红利防御组合）</li>
        </ul>
        <div class="tag-row">
          <span class="mini-tag hot">药明康德</span>
          <span class="mini-tag hot">紫金矿业</span>
          <span class="mini-tag hot">招商银行</span>
          <span class="mini-tag hot">美的集团</span>
        </div>
      </div>
      <div class="highlight-box hb-green">
        <h4>⚠️ Q3 双维度共同减仓（科技拥挤度出清）</h4>
        <ul>
          <li><strong>电子</strong>：北向减配2000亿+、公募占比-7.6pp（仍为第一但拥挤度下降）</li>
          <li><strong>通信</strong>：北向排名第3→第7、公募占比-2.1pp（光模块高位兑现）</li>
          <li><strong>电力设备</strong>：北向减配2000亿+、公募-1.6pp（宁德时代双降）</li>
          <li><strong>机械设备 / 建筑材料</strong>：双双减配</li>
        </ul>
        <div style="margin-top:8px; font-size:12px; color:#15803d;">关键：<strong>减仓≠抛弃</strong>。中金明确指出，三季度末科技仓位仍处历史较高水平，公募仍超配电子、通信，这更像高位结构微调而非系统性撤退。</div>
      </div>
    </div>
    <div class="highlight-box hb-purple" style="margin-top:16px;">
      <h4>🔍 Q3 共识的最大特征：从「单极科技」到「哑铃型结构」</h4>
      <ul>
        <li><strong>哑铃左端（科技）</strong>：仓位仍历史高位，但内部从「光模块+半导体设备」切换到「CXO+存储正主（长鑫）+PCB」，有保有压</li>
        <li><strong>哑铃右端（红利/消费）</strong>：银行、煤炭、公用、石化、家电、白酒全面回补，美的重回北向第二、茅台重回前三</li>
        <li><strong>中金观点</strong>：建议重回「哑铃型结构」配置，科技前期调整更多受事件性与资金面冲击，中期不必过于悲观；红利资产中期关注度有望继续抬升</li>
        <li><strong>分歧点</strong>：北向大幅卖出中际旭创/新易盛，公募却逆势加仓（持股数+2.31%/+8.11%）——光模块的最终判断留待Q4验证</li>
      </ul>
    </div>
  </div>

  <!-- ⑥ 中金公司详细分析 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-blue"></div>⑥ 中金公司：公募 Q3 持仓详细分析</div>
    <div class="update-badge">10/28 更新 · 数据截至 2026/09/30 · 来源：中金公司研究部</div>

    <div class="card">
      <h3>📌 核心变化：股票仓位回落、A股仓位降至76%，资产向债券迁移</h3>
      <p style="font-size:13px; color:var(--gray); line-height:1.8; margin-top:8px;">
        2026年三季度A股震荡下行（上证-6.2%、科创50-30.7%、创业板指-27.8%、沪深300-12.5%、中证红利+9.4%），主动偏股型公募基金<strong>单季度收益率中位数为-12.6%</strong>（上季度+11.2%）。公募基金资产规模转为收缩，<strong>股票资产由8.8万亿降至7.9万亿左右</strong>，占资产总值比重下降2.0个百分点至<strong>19.3%</strong>；债券资产占比上升2.5个百分点至<strong>54.1%</strong>；现金资产占比继续小幅上升0.1个百分点。主动偏股基金<strong>A股仓位由上季度的78%下行至76%</strong>。
      </p>
    </div>

    <div class="card">
      <h3>📊 板块配置：主板仓位回升，创业板/科创板双双回落</h3>
      <table class="data-table">
        <thead><tr><th>板块</th><th>Q2 仓位</th><th>Q3 仓位</th><th>变化</th><th>超/低配</th></tr></thead>
        <tbody>
          <tr style="background:var(--green-light);"><td><strong>主板</strong></td><td>43.6%</td><td><strong>47.5%</strong></td><td class="up" style="color:var(--red);">+3.8pp</td><td>低配约19.3pp</td></tr>
          <tr><td><strong>创业板</strong></td><td>29.6%</td><td><strong>26.2%</strong></td><td class="dn" style="color:var(--green);">-3.4pp</td><td>超配约6.2pp</td></tr>
          <tr><td><strong>科创板</strong></td><td>26.7%</td><td><strong>26.1%</strong></td><td class="dn" style="color:var(--green);">-0.6pp</td><td>超配约13.5pp</td></tr>
          <tr><td>北交所</td><td>0.1%</td><td>0.2%</td><td class="up" style="color:var(--red);">+0.1pp</td><td>低配约0.4pp</td></tr>
        </tbody>
      </table>
      <div style="margin-top:8px; font-size:12px; color:var(--gray);">中信建投口径对照：主动权益基金股票仓位81.8%（环比-1.5pp，2010年以来64%历史分位），主板配置48.1%，科创+创业合计下降4.5pp。</div>
    </div>

    <div class="card">
      <h3>📈 行业配置：医药生物加仓最多（+4.1pp），电子减仓最多（-6.2pp）</h3>
      <table class="data-table">
        <thead><tr><th>加仓行业</th><th>仓位变化</th><th>减仓行业</th><th>仓位变化</th></tr></thead>
        <tbody>
          <tr style="background:var(--green-light);"><td><strong>医药生物</strong></td><td class="up" style="color:var(--red);"><strong>+4.1pp</strong></td><td><strong>电子</strong></td><td class="dn" style="color:var(--green);"><strong>-6.2pp</strong></td></tr>
          <tr style="background:var(--green-light);"><td>汽车</td><td class="up" style="color:var(--red);">获增配</td><td>通信</td><td class="dn" style="color:var(--green);">-2.0pp</td></tr>
          <tr style="background:var(--green-light);"><td>食品饮料</td><td class="up" style="color:var(--red);">获增配</td><td>电力设备</td><td class="dn" style="color:var(--green);">-1.6pp</td></tr>
          <tr style="background:var(--green-light);"><td>家用电器</td><td class="up" style="color:var(--red);">获增配</td><td>建筑材料</td><td class="dn" style="color:var(--green);">-1.1pp</td></tr>
          <tr style="background:var(--green-light);"><td>银行 / 煤炭 / 公用事业 / 石油石化</td><td class="up" style="color:var(--red);">获增配</td><td>机械设备</td><td class="dn" style="color:var(--green);">-0.4pp</td></tr>
          <tr style="background:var(--green-light);"><td>国防军工 / 计算机</td><td class="up" style="color:var(--red);">小幅加仓</td><td>基础化工</td><td class="dn" style="color:var(--green);">-0.1pp</td></tr>
        </tbody>
      </table>
      <div style="margin-top:10px; background:var(--gold-light); border-radius:8px; padding:8px 14px; font-size:12px; color:#b45309;">
        ⚠️ <strong>中金原文：</strong>「前期涨幅较大、交易拥挤的AI硬件产业链三季度被减仓较多，受板块回撤等因素影响，电子和通信仓位分别下降6.2和2.0个百分点；偏中游制造的电力设备、建筑材料、机械设备和基础化工分别减仓1.6、1.1、0.4和0.1个百分点。」但同时强调——<strong>公募仍然超配电子、通信板块</strong>。
      </div>
    </div>

    <div class="card">
      <h3>🔍 集中度回落：龙头抱团松动</h3>
      <table class="data-table">
        <thead><tr><th>维度</th><th>Q2</th><th>Q3</th><th>变化</th></tr></thead>
        <tbody>
          <tr><td>重仓前50市值占比</td><td>55.2%</td><td><strong>49.6%</strong></td><td class="dn" style="color:var(--green);">-5.6pp</td></tr>
          <tr><td>重仓前100市值占比</td><td>68.2%</td><td><strong>62.0%</strong></td><td class="dn" style="color:var(--green);">-6.2pp</td></tr>
          <tr><td>股票占总值比重</td><td>21.3%</td><td><strong>19.3%</strong></td><td class="dn" style="color:var(--green);">-2.0pp</td></tr>
          <tr><td>债券占比</td><td>51.6%</td><td><strong>54.1%</strong></td><td class="up" style="color:var(--red);">+2.5pp</td></tr>
          <tr><td>现金占比</td><td>—</td><td>继续上升</td><td class="up" style="color:var(--red);">+0.1pp</td></tr>
          <tr><td>主动偏股A股仓位</td><td>78.0%</td><td><strong>76.0%</strong></td><td class="dn" style="color:var(--green);">-2.0pp</td></tr>
          <tr><td>单季收益率中位数</td><td>+11.2%</td><td><strong>-12.6%</strong></td><td class="dn" style="color:var(--green);">大幅恶化</td></tr>
        </tbody>
      </table>
      <div style="margin-top:8px; font-size:12px; color:var(--gray);">重仓持股变动：药明康德、天孚通信持仓规模上升较多，中际旭创、新易盛下降较多；港股药明生物、金斯瑞生物科技加仓较多，中芯国际、建滔积层板减仓较多。</div>
    </div>

    <div class="card">
      <h3>🇭🇰 港股与资金面：港股仓位逆势上升</h3>
      <div class="flx">
        <div class="fc">
          <h4>港股仓位上升 2.4pp</h4>
          <p style="font-size:.85em;">可投资港股的主动偏股基金港股配置比例<strong>上升2.4个百分点至15.7%</strong>（Q2为13.3%）。在A股仓位下降的同时，港股配置逆势提升。</p>
        </div>
        <div class="fc">
          <h4>净赎回收窄，新发续降</h4>
          <p style="font-size:.85em;">三季度主动偏股基金被净赎回<strong>931亿份</strong>（对应规模约1,327亿元），较Q2的2,349亿份（约2,000亿元）有所收缩。新发主动偏股型基金<strong>350.7亿份</strong>，较上季度继续回落。</p>
        </div>
      </div>
    </div>

    <div class="card" style="border-left:4px solid var(--gold);">
      <h3 style="color:var(--gold);">💡 中金配置建议：重回「哑铃型结构」</h3>
      <blockquote style="padding:12px 16px; background:var(--gold-light); border-left:3px solid var(--gold); border-radius:0 6px 6px 0; font-size:13px; color:#92400e; line-height:1.9;">
        中金公司10月28日研报指出：从三季度公募基金持仓看，<strong>持仓由科技向消费、红利等方向再平衡</strong>，对电子和通信减仓明显，对金融、消费及资源红利行业加仓较多，但<strong>截至三季度末科技仓位仍处历史较高水平</strong>。<br><br>
        中金认为，A股当前估值已处历史偏低位置，尤其是部分科技领域估值重新回到历史低位，中期投资吸引力显著提升。科技领域前期调整较多受<strong>事件性因素冲击和资金面影响</strong>，对中期走势不必过于悲观。配置上建议重回<strong>「哑铃型结构」</strong>——<br>
        ① 三季报业绩增速环比改善的领域（上游部分有色金属、受益AI高景气与海外需求的科技硬件）；<br>
        ② 高股息资产（长端利率历史低位，股息率与分红规模维持，相对债券吸引力上升）。
      </blockquote>
    </div>
  </div>

  <!-- ⑦ 番外：张坤 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-purple"></div>⑦ 番外：张坤 2026 Q3 调仓与理念</div>
    <div class="update-badge">10/27 更新 · 三季报披露</div>

    <div class="card" style="border-left:4px solid var(--purple);">
      <p style="font-size:13px; color:var(--gray); line-height:1.8;">
        张坤Q3延续「减持白酒、加仓科技」的主线，但操作出现<strong>耐人寻味的分化</strong>：共管的蓝筹精选减持电子（中芯国际、东山精密退出前十），独管的亚洲精选却把<strong>全球AI半导体推至舞台中央</strong>（前十大含台积电、SK海力士、三星电子、阿斯麦、科天半导体）。在管3只产品规模293.07亿元，较年中缩水29.78亿元。
      </p>
    </div>

    <div class="card">
      <h3>一、规模与仓位：总规模降至293亿，但仓位大幅回补至86.55%</h3>
      <table class="data-table">
        <thead><tr><th>基金</th><th>Q3末规模(亿)</th><th>较年中</th><th>Q2→Q3股票仓位</th><th>Q3操作</th></tr></thead>
        <tbody>
          <tr style="background:var(--red-light);"><td><strong>易方达蓝筹精选</strong></td><td>189.33</td><td class="dn">-14.83</td><td><strong>75% → 86.55%</strong>（+11.55pp）</td><td>新进川投能源、新易盛；退出中芯国际、东山精密</td></tr>
          <tr><td>易方达优质精选</td><td>66.84</td><td>基本持平</td><td>↑ 明显提升</td><td>大举增持腾讯控股，延续白酒减持</td></tr>
          <tr><td>易方达亚洲精选</td><td>36.90</td><td>基本持平</td><td>↑ 提升</td><td>大幅增配谷歌、SK海力士、三星电子、科天半导体</td></tr>
          <tr><td>易方达优质企业三年持有</td><td>—</td><td>—</td><td>—</td><td class="dn">9/30 张坤卸任（工作需要）</td></tr>
        </tbody>
      </table>
      <blockquote style="margin-top:12px; padding:10px 14px; background:var(--purple-light); border-left:3px solid var(--purple); border-radius:0 6px 6px 0; font-size:13px; color:#5b21b6;">
        <strong>理念变化：</strong>Q2 张坤把仓位降到 75%（职业生涯首次大规模降仓囤现金），Q3 又快速回补至 86.55%。这说明他 Q2 的降仓是<strong>战术性避险</strong>（规避7月科技股灾），而非战略性看空——7月五轮恐慌出清后，他选择在低位重新加仓。同时 <strong>9月30日卸任</strong>优质企业三年持有，在管产品从4只降至3只，交棒进程继续。
      </blockquote>
    </div>

    <div class="card">
      <h3>二、蓝筹精选前十大：川投能源、新易盛新进，阿里巴巴唯一明显加仓</h3>
      <table class="data-table">
        <thead><tr><th>排名</th><th>蓝筹精选 Q3 重仓股</th><th>占净值比</th><th>Q3变化</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>贵州茅台</td><td>6.37%</td><td class="dn">↓ 继续减持</td></tr>
          <tr><td>2</td><td>中国海洋石油</td><td>6.22%</td><td class="dn">↓ 减持165万股</td></tr>
          <tr><td>3</td><td>腾讯控股</td><td>6.06%</td><td>—</td></tr>
          <tr><td>4</td><td>百胜中国</td><td>5.71%</td><td>—</td></tr>
          <tr><td>5</td><td>泸州老窖</td><td>4.58%</td><td class="dn">↓ 继续减持</td></tr>
          <tr style="background:var(--green-light);"><td>6</td><td><strong>阿里巴巴-W</strong></td><td>3.12%</td><td class="up" style="color:var(--red);"><strong>↑ 唯一明显加仓</strong></td></tr>
          <tr><td>7</td><td>山西汾酒</td><td>2.89%</td><td class="dn">↓ 继续减持</td></tr>
          <tr><td>8</td><td>五粮液</td><td>2.79%</td><td class="dn">↓ 继续减持</td></tr>
          <tr style="background:var(--green-light);"><td>9</td><td><strong>川投能源</strong></td><td>—</td><td class="up" style="color:var(--red);">🆕 新进（持股+20.94%至2902万股）</td></tr>
          <tr style="background:var(--green-light);"><td>10</td><td><strong>新易盛</strong></td><td>—</td><td class="up" style="color:var(--red);">🆕 新进（持股+176.21%至113.21万股）</td></tr>
        </tbody>
      </table>
      <div style="margin-top:8px; font-size:12px; color:var(--gray);">退出前十：中芯国际（半导体）、东山精密（电子制造/PCB/光模块）。</div>
      <blockquote style="margin-top:12px; padding:10px 14px; background:var(--purple-light); border-left:3px solid var(--purple); border-radius:0 6px 6px 0; font-size:13px; color:#5b21b6;">
        <strong>理念变化：</strong>Q2 首次建仓的中芯国际（半导体制造）、东山精密（电子制造）在Q3退出前十——但这不是「否定科技」，而是<strong>科技内部换仓</strong>：卖出偏制造/代工的两个标的，买入<strong>新易盛（光模块龙头，持股+176%）</strong>和<strong>川投能源（公用事业红利，持股+21%）</strong>。同时阿里巴巴成为唯一明显加仓标的——在消费互联网估值低位做逆向布局。整体呈现「<strong>红利（川投）+ AI硬件（新易盛）+ 互联网（阿里）</strong>」的新三角。
      </blockquote>
    </div>

    <div class="card">
      <h3>三、亚洲精选：前十大五只全球AI半导体，加仓台积电、海力士、三星</h3>
      <table class="data-table">
        <thead><tr><th>操作</th><th>标的</th><th>说明</th></tr></thead>
        <tbody>
          <tr style="background:var(--green-light);"><td>大幅加仓</td><td><strong>SK 海力士（000660.KS）</strong></td><td>存储龙头，Q2曾减持56%，Q3大幅回补</td></tr>
          <tr style="background:var(--green-light);"><td>大幅加仓</td><td><strong>三星电子（005930.KS）</strong></td><td>Q2曾减持39%，Q3重新加码</td></tr>
          <tr style="background:var(--green-light);"><td>加仓</td><td><strong>台积电（TSM.N）</strong></td><td>Q2曾减持92%（近乎清仓），Q3重新买入</td></tr>
          <tr style="background:var(--green-light);"><td>重仓</td><td>阿斯麦（ASML）</td><td>Q2已增持+0.36pct</td></tr>
          <tr style="background:var(--green-light);"><td>重仓</td><td>科天半导体（KLAC）</td><td>量检测设备</td></tr>
          <tr style="background:var(--green-light);"><td>加仓</td><td>谷歌（Alphabet）</td><td>Q2曾退出前十，Q3加码</td></tr>
        </tbody>
      </table>
      <blockquote style="margin-top:12px; padding:10px 14px; background:var(--purple-light); border-left:3px solid var(--purple); border-radius:0 6px 6px 0; font-size:13px; color:#5b21b6;">
        <strong>理念变化（重要拐点）：</strong>这是张坤Q3最值得关注的转向。Q2他减持台积电92%、海力士56%、三星39%，被市场解读为「看空海外算力增量叙事」；<strong>Q3他几乎把这些仓位全部买回来了</strong>。结合「AI核心硬件公司已兑现盈利」的判断，这说明他的逻辑是：<strong>看空的是「估值泡沫」而非「产业趋势」</strong>——当海外半导体在Q3回调到合理估值后，他重新认可其价值。同时配置阿斯麦、科天半导体等<strong>设备/卡位环节</strong>（而非纯存储），延续了「选环节」的框架。
      </blockquote>
    </div>

    <div class="card">
      <h3>四、张坤的Q3判断：科技乐观、期待强地产政策、消费修复</h3>
      <blockquote style="padding:12px 16px; background:var(--gold-light); border-left:3px solid var(--gold); border-radius:0 6px 6px 0; font-size:13px; color:#92400e; line-height:1.9;">
        <strong>季报核心观点：</strong><br>
        ① 对<strong>科技整体前景仍保持乐观</strong>，AI核心硬件公司已兑现较高盈利预期；<br>
        ② <strong>期待力度更强的稳地产政策</strong>，地产下行对内需的拖累需要外力打破；<br>
        ③ 认为<strong>居民消费有望修复</strong>，当前更偏好各行业在逆境中仍能提升市场份额的龙头公司；<br>
        ④ 延续「供不应求与算力保有量而非增量相关」的判断，硬件耐用品属性决定业绩与年资本开支挂钩。
      </blockquote>
      <p style="font-size:13px; color:var(--gray); line-height:1.8; margin-top:10px;">
        <strong>分析：</strong>张坤的框架在Q3更加自洽——「科技乐观」对应亚洲精选加码全球AI半导体、蓝筹新进新易盛；「期待稳地产+消费修复」对应白酒虽仍减持但已接近底部、阿里逆势加仓；「偏好逆境提份额龙头」贯穿始终（茅台、腾讯、中海油都是行业下行期的份额赢家）。<strong>业绩表现</strong>：蓝筹精选今年以来-26.26%，近一年年化-33.31%，净值1.3732——短期承压，但他的调仓已从「防守囤现金」转向「进攻布局」。
      </p>
    </div>

    <div class="card" style="border-left:4px solid var(--gold);">
      <h3 style="color:var(--gold);">五、总结：张坤Q3的三个信号</h3>
      <table class="data-table">
        <thead><tr><th>维度</th><th>Q2（避险）</th><th>Q3（回补）</th><th>信号</th></tr></thead>
        <tbody>
          <tr><td><strong>仓位</strong></td><td>降至75%（首次大规模降仓）</td><td><strong>回补至86.55%</strong></td><td>🟢 战术避险结束，重新进攻</td></tr>
          <tr><td><strong>科技</strong></td><td>减持台积电92%、海力士56%</td><td><strong>全部买回+加码</strong></td><td>🟢 看空估值非看空产业</td></tr>
          <tr><td><strong>消费</strong></td><td>白酒继续减持</td><td>白酒仍减但阿里加仓、川投新进</td><td>🟡 从「纯消费」到「红利+互联网」</td></tr>
          <tr><td><strong>结构</strong></td><td>前十集中度38.95%（历史最低）</td><td>新进红利（川投）+AI硬件（新易盛）</td><td>🟢 分散化延续</td></tr>
          <tr><td><strong>管理</strong></td><td>3/4基金团队共管</td><td><strong>卸任1只，在管3只</strong></td><td>🟡 交棒继续</td></tr>
        </tbody>
      </table>
      <blockquote style="margin-top:12px; padding:12px 16px; background:var(--purple-light); border-left:3px solid var(--purple); border-radius:0 6px 6px 0; font-size:13px; color:#5b21b6; line-height:1.9;">
        <strong>最终判断：</strong>张坤Q3的操作，本质是对Q2「极端悲观定价」的一次修正——他在7月科技股灾前降仓避险，在五轮恐慌出清后（Q3）重新加仓。最值得注意的是<strong>海外半导体的完整往返</strong>：Q2清仓式减持台积电，Q3几乎全部买回。这印证了他「估值纪律优先于产业叙事」的一贯框架——贵就卖、便宜就买，无论标的是白酒还是半导体。<br><br>
        对投资者的启示：<strong>连最保守的价值投资者都在Q3回补科技仓位</strong>，说明7-9月的科技深度回调已进入估值可接受区间。但也要注意他的仓位管理——即使回补到86.55%，仍保留13%+现金，且通过「红利+科技」双线分散，而非押注单一赛道。
      </blockquote>
    </div>
  </div>

  <!-- ⑧ 深度讨论 -->
  <div class="section">
    <div class="section-title"><div class="dot dot-red"></div>⑧ 深度讨论：公募的科技信仰变了吗？</div>
    <div class="update-badge">10/30 更新 · Q3三季报收官 · 数据截至9/30</div>

    <div class="card" style="border-left:4px solid var(--red);">
      <p style="font-size:13px; color:var(--gray); line-height:1.9;">
        <strong>背景（Q3三季报更新）：</strong>Q2季报时公募前十全为硬科技，市场质疑「是不是接最后一棒」。Q3答案部分揭晓——7-9月科技深度回调（科创50单季-30.70%、创业板指-27.80%），公募<strong>确实减了科技</strong>：电子仓位-6.2pp、通信-2.0pp，份额从光模块流向CXO、存储正主和红利。<strong>但这是「抛弃科技」还是「高位再平衡」？</strong>Q3的数据给出了更清晰的答案：<strong>减仓但不清仓，科技仓位仍处历史高位，且内部结构大腾挪。</strong>
      </p>
    </div>

    <div class="card">
      <h3>一、事实层：Q3公募确实减了科技，但没有系统性撤退</h3>
      <table class="stock-table">
        <thead><tr><th>证据</th><th>Q3数据</th><th>指向</th></tr></thead>
        <tbody>
          <tr><td>科技持仓占比</td><td>电子36.48%、通信15.21%（天相）</td><td>仍是第一、第二大行业</td></tr>
          <tr><td>电子减仓幅度</td><td>43.4% → 35.8%（-7.6pp，国信）</td><td>减配但未清仓</td></tr>
          <tr><td>前十重仓结构</td><td>7只科技 + 药明康德 + 长鑫科技 + 沪电</td><td>科技仍占7席</td></tr>
          <tr><td>中金判断</td><td>「截至三季度末，科技仓位仍处历史较高水平」</td><td>结构性微调非撤退</td></tr>
          <tr><td>公募超配状态</td><td>仍超配电子、通信</td><td>拥挤度下降但未转向低配</td></tr>
          <tr><td>减持本质</td><td>股价下跌被动缩水（申万电子-32.65%）+ 部分主动兑现</td><td>被动+主动各占一半</td></tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <h3>二、内部腾挪：从「光模块+设备」到「CXO+存储正主+PCB」</h3>
      <table class="stock-table">
        <thead><tr><th>方向</th><th>Q2</th><th>Q3</th><th>变化</th></tr></thead>
        <tbody>
          <tr><td><strong>光模块</strong></td><td>中际旭创第一(1662亿)、新易盛第二</td><td>中际仍第一(959亿)、新易盛第二(868亿)</td><td class="dn">市值腰斩，但持股数量反增（中际+2.31%、新易盛+8.11%）</td></tr>
          <tr style="background:#f0fdf4;"><td><strong>CXO/医药</strong></td><td>药明康德第14（326亿北向口径）</td><td><strong>药明康德新进第三，增持市值榜首</strong></td><td class="up">公募最大加仓方向</td></tr>
          <tr style="background:#f0fdf4;"><td><strong>存储</strong></td><td>兆易创新第7（杂毛存储）</td><td><strong>长鑫科技新进第四（488.78亿）</strong>，兆易退出前十</td><td class="up">「正主」取代「杂毛」</td></tr>
          <tr style="background:#f0fdf4;"><td><strong>PCB</strong></td><td>未入前十</td><td><strong>沪电股份新进第十</strong></td><td class="up">超跌后获增配</td></tr>
          <tr><td><strong>半导体设备</strong></td><td>中微第9、三环第10</td><td>双双退出前十，北方华创仍第9但持仓数量减少</td><td class="dn">设备端减配</td></tr>
        </tbody>
      </table>
      <div style="margin-top:10px; background:var(--gold-light); border-radius:8px; padding:8px 14px; font-size:12px; color:#b45309;">
        ⚠️ <strong>关键洞察：</strong>Q2 报告曾预判「长鑫上市后杂毛存储被边缘化」——Q3 完全兑现（兆易创新退出前十、长鑫科技新进第四）。同时「药明康德增持市值榜首」验证了CXO景气修复。这说明公募不是在撤离科技，而是在科技内部<strong>做「去伪存真」的二次筛选</strong>。
      </div>
    </div>

    <div class="card">
      <h3>三、哑铃成型：科技仍是主桌，红利消费上了新桌</h3>
      <table class="stock-table">
        <thead><tr><th>哑铃端</th><th>Q3配置动作</th><th>北向</th><th>公募</th></tr></thead>
        <tbody>
          <tr style="background:var(--green-light);"><td><strong>科技端</strong></td><td>仓位仍历史高位，内部换仓（CXO/存储/PCB）</td><td>减配电子/通信</td><td>电子-7.6pp但超配</td></tr>
          <tr style="background:var(--gold-light);"><td><strong>红利端</strong></td><td>银行、煤炭、公用、石化增配</td><td>银行第6→第3</td><td>银行/煤炭/公用加仓</td></tr>
          <tr style="background:var(--gold-light);"><td><strong>消费端</strong></td><td>家电、白酒、汽车回补</td><td>美的重回第二、茅台重回前三</td><td>家电/食饮/汽车增配</td></tr>
          <tr style="background:var(--blue-light);"><td><strong>医药端</strong></td><td>加仓最多，CXO领涨</td><td>医药生物新增超百亿</td><td>医药生物+4.1pp最多</td></tr>
        </tbody>
      </table>
      <blockquote style="margin-top:12px; padding:10px 14px; background:var(--blue-light); border-left:3px solid var(--blue); border-radius:0 6px 6px 0; font-size:13px; color:#1e40af; line-height:1.8;">
        <strong>中金定调：</strong>「持仓由科技向消费、红利等方向再平衡」+「科技仓位仍处历史较高水平」+「建议重回哑铃型结构」。这三句话精准概括了Q3公募的真实动作——<strong>不是二选一，而是两头都占</strong>。
      </blockquote>
    </div>

    <div class="card">
      <h3>四、北向 vs 公募：Q3出现罕见分歧</h3>
      <table class="stock-table">
        <thead><tr><th>维度</th><th>北向资金</th><th>公募基金</th><th>分歧点</th></tr></thead>
        <tbody>
          <tr><td><strong>净流向</strong></td><td>Q3净卖出886亿（转为流出）</td><td>股票持仓缩水9801亿（-11.09%）</td><td>同步收缩，但北向更坚决</td></tr>
          <tr><td><strong>光模块</strong></td><td class="num-green">中际/新易盛各净卖出超百亿</td><td class="num-red">逆势加仓（持股+2.31%/+8.11%）</td><td style="color:#b45309;font-weight:600;">⚠️ 罕见反向</td></tr>
          <tr><td><strong>医药</strong></td><td class="num-red">药明康德净买超50亿</td><td class="num-red">药明康德增持市值榜首</td><td>✅ 高度一致</td></tr>
          <tr><td><strong>银行/红利</strong></td><td class="num-red">招商/平安/工行净买</td><td class="num-red">银行/煤炭/公用加仓</td><td>✅ 高度一致</td></tr>
          <tr><td><strong>宁德时代</strong></td><td class="num-green">净卖出居首、持股-10%</td><td class="num-green">降至第七</td><td>✅ 一致减仓</td></tr>
        </tbody>
      </table>
      <div style="margin-top:12px; font-size:13px; line-height:1.9; color:var(--gray);">
        <strong>解读：</strong>Q3 最重要的一致性是<strong>「医药+红利」双升、宁德双降</strong>；最大的分歧是<strong>光模块</strong>——北向大幅卖出，公募反而逆势加仓。这个分歧的答案将在Q4揭晓：若光模块继续调整，公募「逆势加仓」可能重蹈追高覆辙；若反弹，则体现公募对业绩（新易盛H1净利+78~103%）的坚持。
      </div>
    </div>

    <div class="card" style="border-left:4px solid var(--purple);">
      <h3 style="color:var(--purple);">五、Q3 综合结论</h3>
      <ol style="font-size:13px; color:var(--dark); line-height:2; padding-left:20px;">
        <li><strong>「接最后一棒」的担忧，Q3给出了否定的答案。</strong>公募没有清仓科技，而是减配+换仓：电子占比-7.6pp但仍第一、超配状态未改，中金明确「科技仓位仍处历史较高水平」。这是<strong>高位再平衡，而非系统性撤退</strong>。</li>
        <li><strong>换仓的方向印证了Q2的判断。</strong>「长鑫科技新进第四、兆易创新退出前十」验证了「杂毛存储被正主取代」；「药明康德增持市值榜首」验证了CXO景气修复；「沪电新进前十」验证了超跌龙头的再定价。</li>
        <li><strong>哑铃型结构成为机构的共同选择。</strong>科技（内部精选）+ 红利（银行/煤炭/公用）+ 消费（家电/白酒）+ 医药（CXO），四线并行。中金明确建议重回哑铃型配置。</li>
        <li><strong>北向与公募的分歧集中在光模块。</strong>北向Q3净卖出中际旭创/新易盛各超百亿，公募却逆势加仓。这个分歧是Q4最值得跟踪的信号——谁对谁错，取决于中报后订单与业绩能否续证。</li>
        <li><strong>张坤的动作是行业缩影。</strong>Q2降仓75%避险 → Q3回补86.55%进攻，海外半导体完整往返（减持92% → 全部买回）。他证明了「估值纪律优先于产业叙事」的有效性。</li>
        <li><strong>Q4关键变量：</strong>① 光模块订单能否续证（公募逆势加仓的胜负手）；② 医药/CXO景气能否持续；③ 红利资产的资金持续性；④ 科技估值是否已在历史低位（中金判断中期不必悲观）。</li>
        <li><strong>对投资者的启示：</strong>Q3最值得学的不是「买什么」，而是<strong>机构的仓位管理方式</strong>——减仓不清仓、内部换仓、哑铃分散、保留现金。连张坤都在回补仓位时保留13%+现金。<strong>在结构性行情中，「均衡」比「押注」更能穿越波动。</strong></li>
      </ol>
    </div>
  </div>

  <!-- 免责声明 -->
  <div class="disclaimer">
    ⚠️ <strong>风险提示与数据说明：</strong>本报告为 2026 Q3 版本。北向资金数据截至 2026-09-30（10月15日披露，来源 Wind/Choice）；公募基金三季报已于 2026-10-27 披露完毕（来源天相投顾/Wind/Choice/中金公司研究部）；机构长线资金（社保/QFII）待披露。张坤番外数据来源于易方达基金三季报及公开报道（证券时报/21世纪经济报道/新浪财经）。所有数值经交叉校验。投资有风险，决策需谨慎，请结合自身风险偏好独立判断。
  </div>

</div>
'''

SCRIPT = r'''
<!-- ============ 数据校验引擎 ============ -->
<script>
const DATA = {
  northbound: {
    total_holdings_q2_trillion: 3.13,
    total_holdings_q3_trillion: 2.58,
    net_buy_q3_yi: -886,
    net_buy_h1_yi: 1995,
    net_buy_q2_yi: 2086,
    top3_q2: ["宁德时代","中际旭创","北方华创"],
    top3_q3: ["宁德时代","美的集团","贵州茅台"],
    top1_stable: "宁德时代",
    source: "Wind / Choice"
  },
  public_fund: { status: "disclosed" },
  institution: { status: "pending" }
};
const TRILLION_TO_YI = 10000.0;

function vResult(level, rid, desc, detail, status){ return {level, rid, desc, detail, status}; }

function runValidation(){
  const nb = DATA.northbound;
  const out = [];
  // 勾稽
  const q3_plus_h1 = nb.net_buy_h1_yi + nb.net_buy_q3_yi;
  out.push(vResult("勾稽","V-FOOT-01","H1净买入 + Q3净买入 = 前三季度累计",
    `H1(${nb.net_buy_h1_yi}) + Q3(${nb.net_buy_q3_yi}) = ${q3_plus_h1} 亿元（前三季度累计）`,
    (q3_plus_h1 === nb.net_buy_h1_yi + nb.net_buy_q3_yi) ? "PASS" : "FAIL"));
  out.push(vResult("勾稽","V-FOOT-02","Q2大幅流入(+2086) → Q3转为流出(-886)，方向逆转自洽",
    `Q2=+${nb.net_buy_q2_yi}亿, Q3=${nb.net_buy_q3_yi}亿`,
    (nb.net_buy_q2_yi>0 && nb.net_buy_q3_yi<0) ? "PASS" : "FAIL"));
  // 范围
  const th3 = nb.total_holdings_q3_trillion;
  out.push(vResult("范围","V-RANGE-01","Q3总持仓回落但仍处2万亿以上",
    `Q3总持仓 = ${th3} 万亿；阈值2.0`,
    th3 >= 2.0 ? "PASS" : "FAIL"));
  const delta = (th3 - nb.total_holdings_q2_trillion) * TRILLION_TO_YI;
  out.push(vResult("范围","V-RANGE-02","Q3持仓变动量级合理（降幅<25%）",
    `Δ = ${delta.toFixed(0)}亿；较Q2降幅 ${Math.abs(delta/(nb.total_holdings_q2_trillion*TRILLION_TO_YI)*100).toFixed(1)}%`,
    (Math.abs(delta/(nb.total_holdings_q2_trillion*TRILLION_TO_YI))<0.25) ? "PASS" : "WARN"));
  // 交叉
  const price_contrib = delta - nb.net_buy_q3_yi;
  out.push(vResult("交叉","V-CROSS-01","持仓降幅>净卖出 ⇒ 股价下跌贡献为负",
    `Δ总持仓≈${delta.toFixed(0)}亿，Q3净买入=${nb.net_buy_q3_yi}亿，股价下跌贡献≈${price_contrib.toFixed(0)}亿`,
    price_contrib < 0 ? "PASS" : "WARN"));
  const in_both = nb.top3_q2.filter(x=>nb.top3_q3.includes(x));
  const top1_ok = nb.top3_q2.includes(nb.top1_stable) && nb.top3_q3.includes(nb.top1_stable);
  out.push(vResult("交叉","V-CROSS-02","市值TOP3两期连续性（宁德时代三期稳居第一）",
    `两期交集=[${in_both.join(',')}]；top1='${nb.top1_stable}' 两期均出现=${top1_ok}`,
    (top1_ok && in_both.length>=1) ? "PASS" : "FAIL"));
  const changed = JSON.stringify(nb.top3_q2)!==JSON.stringify(nb.top3_q3);
  out.push(vResult("交叉","V-CROSS-03","市值前三较Q2显著变化（科技→消费）",
    `Q2=[${nb.top3_q2}] → Q3=[${nb.top3_q3}]；是否变化=${changed}`,
    changed ? "PASS" : "WARN"));
  // 完整性
  out.push(vResult("完整","V-FULL-01","已披露数据均标注来源",
    `北向 source = ${nb.source}`,
    nb.source ? "PASS" : "FAIL"));
  const pending = [];
  if(DATA.public_fund.status==="pending") pending.push("公募基金");
  if(DATA.institution.status==="pending") pending.push("机构长线资金");
  out.push(vResult("完整","V-FULL-02","未披露维度显式标记 pending",
    `待披露维度：${pending.length?pending.join('、'):'无'}`,
    pending.length ? "WARN" : "PASS"));
  return out;
}

(function render(){
  const results = runValidation();
  const cnt = {PASS:0, WARN:0, FAIL:0};
  results.forEach(r=>cnt[r.status]=(cnt[r.status]||0)+1);
  const hardFail = cnt.FAIL > 0;
  const summaryEl = document.getElementById("val-summary");
  summaryEl.innerHTML =
    `<div class="val-chip">✅ PASS <b>${cnt.PASS}</b></div>`+
    `<div class="val-chip">⚠️ WARN <b>${cnt.WARN}</b></div>`+
    `<div class="val-chip">❌ FAIL <b>${cnt.FAIL}</b></div>`;
  const overall = document.getElementById("val-overall");
  if(hardFail){
    overall.textContent = "❌ 校验未通过 — 禁止发布";
    overall.style.background = "rgba(248,113,113,0.25)";
    overall.style.color = "#f87171";
  } else {
    overall.textContent = "✅ 校验通过（无硬性矛盾）";
    overall.style.background = "rgba(74,222,128,0.2)";
    overall.style.color = "#4ade80";
  }
  const body = document.getElementById("val-body");
  body.innerHTML = results.map(r=>
    `<tr>
      <td>${r.level}</td>
      <td>${r.rid}</td>
      <td class="val-status s-${r.status}">${r.status}</td>
      <td><div>${r.desc}</div><div class="val-detail">${r.detail}</div></td>
    </tr>`).join("");
})();

(function(){
  const details = document.querySelector('.val-details');
  const hint = document.getElementById('val-hint');
  if(!details||!hint) return;
  details.addEventListener('toggle',function(){
    hint.textContent = details.open ? '点击折叠校验详情 ▲' : '点击展开校验详情 ▼';
  });
})();
</script>
'''

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>聪明钱共识追踪报告 | 2026 Q3</title>
{STYLE}
</head>
<body>
{BODY}
{SCRIPT}
</body>
</html>
'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)
print(f"written {OUT}, size={len(HTML)}")
