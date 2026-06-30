#!/usr/bin/env python3
"""生成半导体分析报告 HTML"""
import pandas as pd, json, os

OUT='/Users/yntwt/feasibility-analysis-strategy/data'
df=pd.read_csv(f'{OUT}/batch1_quotes.csv')
df['trade_date']=df['trade_date'].astype(str)

# === 关键标的价格提取 ===
def price(code,date):
    r=df[(df['ts_code']==code)&(df['trade_date']==date)]
    return round(r.iloc[0].close,2) if len(r)>0 else None

def chg_pct(code,d1,d2):
    p1,p2=price(code,d1),price(code,d2)
    if p1 and p2: return round((p2-p1)/p1*100,1)
    return None

# 核心标的
TICKERS={
    '002371.SZ':('北方华创','设备'),'688012.SH':('中微公司','设备'),'688072.SH':('拓荆科技','设备'),
    '688126.SH':('沪硅产业','材料'),'688019.SH':('安集科技','材料'),'002409.SZ':('雅克科技','材料'),
    '300666.SZ':('江丰电子','材料'),'002312.SZ':('鼎龙股份','材料'),'688720.SH':('艾森股份','材料'),
    '688981.SH':('中芯国际','晶圆'),'688347.SH':('华虹半导体','晶圆'),
    '688200.SH':('华峰测控','设备'),'688082.SH':('盛美上海','设备'),
    '601133.SH':('柏诚股份','洁净室'),'603859.SH':('能科科技','洁净室'),
    '603998.SH':('方邦股份','材料'),
}

# === 数值计算 ===
today_d={'002371':813.37,'688012':413,'688072':832,'688126':34.86,'688019':274.48,
         '002409':188.6,'300666':354.78,'002312':10.11,'688720':94.26,'688981':148.76,
         '688347':323,'688200':469.1,'688082':414,'601133':38.28,'603859':46.91,'603998':8.85}

today_chg={'002371':1.93,'688012':3.48,'688072':1.09,'688126':4.65,'688019':2.21,
           '002409':4.18,'300666':7.51,'002312':-1.65,'688720':6.87,'688981':-5.16,
           '688347':-2.23,'688200':3.16,'688082':0.25,'601133':10.0,'603859':-3.02,'603998':-4.01}

rows_eq=[]
for code,(name,cat) in TICKERS.items():
    short=code[:6]
    r={
        'name':name,'cat':cat,'code':code,
        'p_0606':price(code,'20260506'),'p_0626':price(code,'20260626'),
        'p_today':today_d.get(short),'chg_today':today_chg.get(short),
        'chg_56_26':chg_pct(code,'20260506','20260626'),
        'chg_608_626':chg_pct(code,'20260608','20260626'),
    }
    rows_eq.append(r)

# === 生成HTML表格行 ===
def row_html(r,show_all=False):
    p_t=r.get('p_today','-')
    chg_t=r.get('chg_today','-')
    cls_up='up' if isinstance(chg_t,(int,float)) and chg_t>0 else ('dn' if isinstance(chg_t,(int,float)) and chg_t<0 else '')
    chg_s=f'<span class="{cls_up}">{chg_t:+.1f}%' if isinstance(chg_t,(int,float)) else '-'
    
    chg56=r.get('chg_56_26','-')
    cls56='up' if isinstance(chg56,(int,float)) and chg56>0 else 'dn'
    chg56_s=f'<span class="{cls56}">{chg56:+.1f}%' if isinstance(chg56,(int,float)) else '-'
    
    chg68=r.get('chg_608_626','-')
    cls68='up' if isinstance(chg68,(int,float)) and chg68>0 else 'dn'
    chg68_s=f'<span class="{cls68}">{chg68:+.1f}%' if isinstance(chg68,(int,float)) else '-'
    
    # 6/26 close price
    p0626=r.get('p_0626','-')
    # 5/6 price for context
    p0506=r.get('p_0606','-')
    
    risk_tag=''
    if isinstance(chg56,(int,float)):
        if chg56>80: risk_tag=' <span class="tr">⚠高风险</span>'
        elif chg56>50: risk_tag=' <span class="tg">⚡中风险</span>'
    
    code_short=r['code'][:6]
    return f"""<tr><td><a href="https://quote.eastmoney.com/{'sz' if code_short.startswith(('0','3')) else 'sh'}{code_short}.html" target="_blank" class="sk"><strong>{r['name']} {code_short}</strong></a></td>
    <td>{p0506}</td><td>{p0626}</td><td class="num"><strong>{p_t}</strong></td>
    <td class="num">{chg_s}</td>
    <td class="num">{chg56_s}{risk_tag}</td>
    <td class="num">{chg68_s}</td></tr>"""

# 分类
equip=[r for r in rows_eq if r['cat']=='设备']
material=[r for r in rows_eq if r['cat']=='材料']
fab=[r for r in rows_eq if r['cat']=='晶圆']
clean=[r for r in rows_eq if r['cat']=='洁净室']

# === 材料板块重点关注 ===
mat_warn=[]
for r in rows_eq:
    if r['cat']=='材料':
        chg56=r.get('chg_56_26')
        if isinstance(chg56,(int,float)):
            if chg56>80: mat_warn.append(f"{r['name']}({r['code'][:6]}) 5/6→6/26涨幅{chg56:+.1f}%，波动极值区间需警惕获利回吐")
            elif chg56>50: mat_warn.append(f"{r['name']}({r['code'][:6]}) 5/6→6/26涨幅{chg56:+.1f}%，短期涨幅过大注意节奏")

equip_rows=''.join(row_html(r) for r in equip)
mat_rows=''.join(row_html(r) for r in material)
fab_rows=''.join(row_html(r) for r in fab)
clean_rows=''.join(row_html(r) for r in clean)
mat_warn_html='<br>'.join(f'<li>{w}</li>' for w in mat_warn) if mat_warn else '<li>材料板块整体风险可控</li>'

# 材料股全景
mat_full_rows=''.join(row_html(r) for r in sorted(rows_eq,key=lambda x: x['chg_56_26'] or -999, reverse=True) if r['cat']=='材料')

# 雅克科技波段数据验证 (从 raw df 取)
ya_df=df[df['ts_code']=='002409.SZ'].sort_values('trade_date')
ja_df=df[df['ts_code']=='300666.SZ'].sort_values('trade_date')

# === HTML ===
html=f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>半导体扩产阳谋：产业链重估与操作框架（更新至6/29）</title>
<style>
:root{{--bg:#0f1117;--c:#1a1d28;--b:#2a2d3a;--t:#e1e4ea;--t2:#8b8fa3;--r:#e15241;--g:#22c55e;--a:#4fc3f7;--o:#f59e0b;--p:#a78bfa;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--t);font-family:-apple-system,"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.85;padding:20px;max-width:1100px;margin:0 auto;}}
h1{{font-size:1.7em;text-align:center;padding:28px 0 24px;border-bottom:2px solid var(--a);margin-bottom:20px;}}
h2{{font-size:1.3em;color:var(--a);margin:35px 0 16px;padding-left:12px;border-left:3px solid var(--a);}}
h3{{font-size:1.1em;color:var(--o);margin:20px 0 12px;}}
.card{{background:var(--c);border:1px solid var(--b);border-radius:10px;padding:20px 24px;margin:16px 0;}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:0.88em;}}
th{{background:#252836;color:var(--a);padding:9px 10px;text-align:left;font-weight:600;border-bottom:2px solid var(--b);}}
td{{padding:8px 10px;border-bottom:1px solid var(--b);}}
tr:hover td{{background:rgba(79,195,247,0.04);}}
blockquote{{background:rgba(79,195,247,0.06);border-left:3px solid var(--a);padding:10px 16px;margin:12px 0;color:var(--t2);font-size:0.93em;border-radius:0 6px 6px 0;line-height:1.75;}}
.qo{{border-left-color:var(--o);background:rgba(245,158,11,0.06);}}
.qp{{border-left-color:var(--p);background:rgba(167,139,250,0.06);}}
ul,ol{{padding-left:24px;margin:8px 0;}}li{{margin:6px 0;}}
a{{color:var(--a);text-decoration:none;}}.sk{{color:inherit;text-decoration:none;border-bottom:1px dotted var(--a);}}.sk:hover{{color:var(--a);}}
.back{{display:inline-block;margin-bottom:20px;color:var(--t2);font-size:0.88em;text-decoration:none;}}.back:hover{{color:var(--a);}}
.meta{{display:flex;justify-content:center;flex-wrap:wrap;gap:10px;margin-bottom:22px;}}
.meta span{{color:var(--t2);font-size:0.83em;padding:3px 10px;background:rgba(79,195,247,0.05);border-radius:12px;border:1px solid var(--b);}}
.up{{color:var(--r);font-weight:600;}}.dn{{color:var(--g);font-weight:600;}}
.warn{{background:rgba(245,158,11,0.08);border-left:4px solid var(--o);padding:12px 16px;border-radius:0 8px 8px 0;margin:12px 0;font-size:0.91em;}}
.danger{{background:rgba(226,82,65,0.08);border-left:4px solid var(--r);padding:12px 16px;border-radius:0 8px 8px 0;margin:12px 0;font-size:0.91em;}}
.verdict{{background:linear-gradient(135deg,rgba(167,139,250,0.08),rgba(79,195,247,0.08));border-left:4px solid var(--p);padding:18px 22px;border-radius:0 10px 10px 0;margin:16px 0;}}
.flx{{display:flex;gap:14px;flex-wrap:wrap;margin:12px 0;}}
.fc{{flex:1;min-width:250px;background:rgba(79,195,247,0.03);border:1px solid var(--b);border-radius:10px;padding:16px;}}.fc h4{{margin-top:0;color:var(--o);}}
.kv{{background:#0c1017;border:1px solid var(--b);border-radius:8px;padding:16px 20px;margin:14px 0;font-family:'SF Mono','Consolas',monospace;font-size:0.84em;overflow-x:auto;line-height:2;}}
.kv .l{{color:var(--t2);}}.kv .R{{color:var(--r);}}.kv .G{{color:var(--g);}}.kv .S{{color:var(--o);}}.kv .P{{color:var(--p);}}.kv .B{{color:var(--a);}}
.tag{{display:inline-block;padding:3px 10px;border-radius:12px;font-size:0.8em;margin:2px 4px;}}
.tr{{background:rgba(226,82,65,0.15);color:var(--r);}}.tg{{background:rgba(245,158,11,0.15);color:var(--o);}}.tgr{{background:rgba(34,197,94,0.15);color:var(--g);}}
.footer{{color:var(--t2);font-size:0.84em;text-align:center;margin-top:28px;padding-top:18px;border-top:1px solid var(--b);}}
@media(max-width:768px){{body{{padding:12px}}h1{{font-size:1.3em}}h2{{font-size:1.1em}}table{{font-size:0.75em}}th,td{{padding:5px 6px}}}}
</style></head><body>

<a href="./index.html" class="back">← 返回首页</a>

<h1>🔬 半导体扩产阳谋：产业链重估与操作框架</h1>
<div class="meta">
  <span>数据截止：2026-06-29 收盘</span>
  <span>更新至今日最新</span>
  <span>Tushare Pro 行情数据</span>
</div>

<blockquote class="qo">
  <strong>文章来源：</strong><br>
  ① <a href="https://mp.weixin.qq.com/s/0RzSIQt_KBPZRQvFDu67vQ" target="_blank">《半导体扩产潮来了》</a> — 张博 &nbsp;|&nbsp;
  ② <a href="https://mp.weixin.qq.com/s/Ek_Pumo7hb7P_j2afjn2mg" target="_blank">《中国半导体的阳谋》</a> — 董必政<br>
  中国半导体最重要的故事，已经不只是某一台设备有没有突破，而是一批晶圆厂正在<strong>同步扩建、融资、导入设备、重构供应链</strong>。真正值得问的问题已经不是"半导体行不行"，而是这一轮扩产，<strong>投资机会到底会沿着什么链条释放？</strong>
</blockquote>

<!-- ===== 一：扩产全景 ===== -->
<h2>一、扩产全景：从"追单点"到"建体系"</h2>

<div class="card">
  <h3>📊 四大晶圆厂 2026 扩产数据</h3>
  <table>
    <thead><tr><th>晶圆厂</th><th>2026Q1业绩</th><th>扩产节奏</th><th>Capex规模</th></tr></thead>
    <tbody>
      <tr><td><strong>长鑫科技</strong> (DRAM)</td><td>营收<span class="up">508亿(+719%)</span>，净利<span class="up">247.6亿</span></td><td>IPO募295亿；H1预计净利500-570亿</td><td>目标产能60-70万片/月，未来需投3000亿+</td></tr>
      <tr><td><strong>长江存储</strong> (NAND)</td><td>年产177万片→2026E近200万片</td><td>Xtacking4.0 294层量产，良率>90%</td><td>Q2启动设备招标</td></tr>
      <tr><td><a href="https://quote.eastmoney.com/sh688981.html" target="_blank" class="sk"><strong>中芯国际 688981</strong></a></td><td>月产108万片(8")，利用率93.1%</td><td>折旧占比升至44%</td><td>全年约80亿美元</td></tr>
      <tr><td><a href="https://quote.eastmoney.com/sh688347.html" target="_blank" class="sk"><strong>华虹半导体 688347</strong></a></td><td>利用率99.7%，12"收入占62.7%</td><td>Fab9A Q3满产，Fab9B 3月开工</td><td>Fab9B 60亿美元</td></tr>
    </tbody>
  </table>
</div>

<blockquote>
  因为晶圆厂不是一个单一项目，而是整个半导体产业链最强的<strong>"投资放大器"</strong>。一座晶圆厂的建设，会同时拉动洁净室工程、刻蚀和沉积设备、检测设备、硅片、光刻胶、电子特气、CMP材料、靶材、零部件——每往前走一步，上游就会有一批公司进入兑现周期。
</blockquote>

<!-- ===== 二：机会分层 ===== -->
<h2>二、机会分层：谁先兑现，谁弹性最大？</h2>

<blockquote class="qo">
  机会从来不是平均分配的，而是<strong>分层兑现、节奏不同、风险不同</strong>。
</blockquote>

<div class="kv"><span class="l">──────── 扩产红利释放顺序 ────────</span>
<span class="l">第一层</span> <span class="B">🏗️ 洁净室/工程</span> <span class="l">→</span> <span class="tgr">最早兑现</span> <span class="l">项目落地快、收入确认早</span>
<span class="l">第二层</span> <span class="B">⚙️ 半导体设备</span> <span class="l">→</span> <span class="tr">弹性最大</span> <span class="l">Capex占比最高</span>
<span class="l">第三层</span> <span class="B">🧪 半导体材料</span> <span class="l">→</span> <span class="tg">穿越周期</span> <span class="l">复购属性强+客户黏性高</span>
<span class="l">第四层</span> <span class="B">🔧 EDA/零部件</span> <span class="l">→</span> <span class="P">中长期布局</span> <span class="l">依赖生态成熟</span></div>

<!-- ===== 设备 ===== -->
<h2>三、设备：弹性最大（核心战场）</h2>

<div class="card">
  <h3>⚙️ 核心设备股 — 5/6 → 6/26 → 6/29 价格追踪</h3>
  <table>
    <thead><tr><th>公司</th><th>5/6起点</th><th>6/26收盘</th><th>6/29收盘</th><th>6/29涨跌</th><th>5/6→6/26总涨幅</th><th>6/8低点反弹</th></tr></thead>
    <tbody>{equip_rows}</tbody>
  </table>
  <blockquote class="qo"><strong>关键发现：</strong>设备板块「盛美上海」「拓荆科技」涨幅分别达163.4%、79.2%，证明设备仍是扩产弹性最大的环节。但注意盛美上海涨幅已极度偏离均线，需警惕短线获利回吐。</blockquote>
</div>

<!-- ===== 材料（重点扩展） ===== -->
<h2>四、🧪 半导体材料：穿越周期的核心变量（重点扩展）</h2>

<blockquote class="qp">
  <strong>为什么材料至关重要？</strong><br>
  设备是一次性采购，而材料是<strong>持续消耗品</strong>——只要有晶圆厂在运转，就需要源源不断的硅片、光刻胶、CMP抛光液、电子特气、靶材。材料的商业模式天然具备更强的<strong>复购属性和客户黏性</strong>。晶圆厂扩产 → 产能爬坡 → 材料用量同步增长 → 材料企业业绩进入释放期。<br><br>
  <strong>本报告将材料股覆盖范围从原报告的2只扩展至6只</strong>：沪硅产业(大硅片)、安集科技(CMP抛光液)、雅克科技(前驱体/光刻胶)、江丰电子(高纯靶材)、鼎龙股份(CMP抛光垫)、艾森股份(电镀液)。
</blockquote>

<div class="card">
  <h3>🧪 半导体材料股全景（5/6 → 6/29）</h3>
  <table>
    <thead><tr><th>公司</th><th>5/6起点</th><th>6/26收盘</th><th>6/29收盘</th><th>6/29涨跌</th><th>5/6→6/26</th><th>6/8低点反弹</th></tr></thead>
    <tbody>{mat_full_rows}</tbody>
  </table>
</div>

<div class="flx">
  <div class="fc"><h4>🥇 材料涨幅王：雅克科技 +109.1%</h4>
    <p style="color:var(--t2);font-size:0.88em;">前驱体+光刻胶双主线布局，长鑫/长存扩产直接受益。6/8低点47.8→6/26收85.3，反弹+78.6%，量价配合良好。</p>
  </div>
  <div class="fc"><h4>🥈 靶材龙头：江丰电子 +94.9%</h4>
    <p style="color:var(--t2);font-size:0.88em;">高纯溅射靶材进口替代核心标的。6/8低点93.3→6/26收171.0，反弹+83.3%，材料中弹性第一。</p>
  </div>
  <div class="fc"><h4>🥉 大硅片：沪硅产业 +56.1%</h4>
    <p style="color:var(--t2);font-size:0.88em;">300mm硅片放量，产能爬坡中。6/8低点15.22→6/26收20.42，虽亏损但市场愿为产能扩张付费。</p>
  </div>
</div>

<div class="danger">
  <strong>⚠️ 材料板块风险警示：</strong><br>
  <ol>{mat_warn_html}</ol>
</div>

<!-- ===== 晶圆厂 ===== -->
<h2>五、晶圆厂：链主定价权</h2>

<div class="card">
  <h3>🏭 晶圆厂 5/6 → 6/29 价格追踪</h3>
  <table>
    <thead><tr><th>公司</th><th>5/6起点</th><th>6/26收盘</th><th>6/29收盘</th><th>6/29涨跌</th><th>5/6→6/26</th><th>6/8低点反弹</th></tr></thead>
    <tbody>{fab_rows}</tbody>
  </table>
</div>

<!-- ===== 洁净室 ===== -->
<h2>六、洁净室：最早兑现</h2>
<div class="card">
  <h3>🏗️ 洁净室工程</h3>
  <table>
    <thead><tr><th>公司</th><th>5/6起点</th><th>6/26收盘</th><th>6/29收盘</th><th>6/29涨跌</th><th>5/6→6/26</th><th>6/8低点反弹</th></tr></thead>
    <tbody>{clean_rows}</tbody>
  </table>
  <blockquote>柏诚股份 6/29 <span class="up">涨停 +10%</span>，是最早进入到兑现周期的洁净室概念。</blockquote>
</div>

<!-- ===== 估值审视 ===== -->
<h2>七、估值审视与风险量化</h2>

<div class="card">
  <h3>📐 5/6→6/26 涨幅分布与风险评级</h3>
  <table>
    <thead><tr><th>风险等级</th><th>涨幅区间</th><th>标的</th><th>风险提示</th></tr></thead>
    <tbody>
      <tr style="background:rgba(226,82,65,0.06);"><td><span class="tr">⚠ 高风险</span></td><td>&gt;80%</td><td>盛美上海(163.4%)、华虹半导体(112.5%)、雅克科技(109.1%)</td><td>短期涨幅严重偏离均线，回调压力极大</td></tr>
      <tr style="background:rgba(245,158,11,0.06);"><td><span class="tg">⚡ 中风险</span></td><td>50-80%</td><td>江丰电子(94.9%)、拓荆科技(79.2%)、柏诚股份(61.1%)、沪硅产业(56.1%)</td><td>趋势尚在但需控制仓位</td></tr>
      <tr><td><span class="tgr">🟢 低风险</span></td><td>&lt;50%</td><td>北方华创(49.1%)、中微公司(7.7%)、安集科技(5.6%)</td><td>补涨空间更大</td></tr>
    </tbody>
  </table>
</div>

<!-- ===== 操作框架 ===== -->
<h2>八、操作框架与纪律</h2>

<div class="flx">
  <div class="fc"><h4>🟢 当前性价比优选</h4>
    <ul>
      <li><strong>北方华创 002371</strong> — 813.37，全区间+49.1%，平台型龙头仍被低估</li>
      <li><strong>中微公司 688012</strong> — 413.00，全区间仅+7.7%，补涨动能最大</li>
      <li><strong>安集科技 688019</strong> — 274.48，全区间+5.6%，估值最合理的材料股</li>
    </ul></div>
  <div class="fc"><h4>🟡 激进但需止盈</h4>
    <ul>
      <li><strong>雅克科技 002409</strong> — 188.60，+109.1%，设30%止盈线</li>
      <li><strong>江丰电子 300666</strong> — 354.78，+94.9%，今日+7.51%</li>
      <li><strong>拓荆科技 688072</strong> — 832.00，+79.2%，注意短线压力</li>
    </ul></div>
  <div class="fc"><h4>📋 操作纪律</h4>
    <table style="margin:0;"><tr><td>止盈</td><td>浮盈>30%减20%</td></tr><tr><td>止损</td><td>跌破MA60清仓</td></tr><tr><td>追高禁区</td><td>舆情最热时不追</td></tr><tr><td>材料龙头</td><td>安集科技/沪硅产业优先</td></tr></table></div>
</div>

<hr>

<div class="verdict">
  <strong>📊 综合总结（更新至6/29收盘）</strong><br><br>

  <strong>一、6月主线行情加速验证</strong><br>
  5/6起点至今，16只标的平均涨幅+58.4%，其中盛美上海暴涨+163.4%、华虹半导体+112.5%、雅克科技+109.1%。6/8低点反弹数据显示，材料股江丰电子(+83.3%)和雅克科技(+78.6%)反弹弹性甚至超过设备股——材料板块正在成为第二波主升浪的<strong>新旗手</strong>。<br><br>

  <strong>二、材料股从配角变为主角</strong><br>
  扩产逻辑从「设备一次性采购」延伸至「材料持续消耗」——晶圆厂产能爬坡意味着材料用量的<strong>线性增长</strong>。雅克科技和江丰电子在6月的表现远超设备股均值，验证了材料板块的穿越周期属性。<br><br>

  <strong>三、今日（6/29）市场信号</strong><br>
  柏诚股份<span class="up">涨停+10%</span>（洁净室早期兑现）、江丰电子<span class="up">+7.51%</span>（靶材）、艾森股份<span class="up">+6.87%</span>（电镀液）。材料股联动上涨，钱在往材料方向集中。但中芯国际<span class="dn">-5.16%</span>、华虹半导体<span class="dn">-2.23%</span>出现晶圆厂分化，提示市场正在精细化定价，不是普涨。<br><br>

  <strong>四、操作建议</strong><br>
  当前主线明确但高低分化加剧。对待暴涨股（盛美/雅克/江丰）应严设止盈，不追高；对待补涨股（中微/安集/北方华创）可在回调时分批建仓。材料板块长期逻辑畅通，但短期涨幅过大需要有一个消化过程。
</div>

<div class="footer">
  核心信源：虎嗅APP — <a href="https://mp.weixin.qq.com/s/0RzSIQt_KBPZRQvFDu67vQ">半导体扩产潮来了</a> & <a href="https://mp.weixin.qq.com/s/Ek_Pumo7hb7P_j2afjn2mg">中国半导体的阳谋</a><br>
  行情数据：Tushare Pro（2026-06-29 收盘，覆盖 5/6 ~ 6/29 全部交易日）<br>
  ⚠️ 仅供参考，不构成投资建议。股市有风险，投资需谨慎。
</div>

</body></html>"""

with open('/Users/yntwt/feasibility-analysis-strategy/semiconductor_expansion_deep_dive_20260629.html','w',encoding='utf-8') as f:
    f.write(html)
print(f'✅ 报告已生成：{len(html)} 字符')
