#!/usr/bin/env python3
"""数据分析汇总：半导体产业链重估"""
import pandas as pd, numpy as np, json, os

OUT='/Users/yntwt/feasibility-analysis-strategy/data'
df=pd.read_csv(f'{OUT}/batch1_quotes.csv')
df['trade_date']=df['trade_date'].astype(str)

# 关键时点提取
dates=['20260506','20260529','20260601','20260608','20260615','20260623','20260626']
latest=df[df['trade_date']=='20260626'].copy()

# 每个标的计算阶段涨跌幅
results=[]
for code,g in df.groupby('ts_code'):
    g=g.sort_values('trade_date')
    name=g.iloc[-1]['name']
    r={'code':code,'name':name}
    for d in dates:
        row=g[g['trade_date']==d]
        if len(row)>0: r[f'close_{d}']=round(row.iloc[0].close,2)
    # 阶段涨幅
    for (a,b,lbl) in [('20260506','20260529','5/6→5/29'),('20260529','20260626','5/29→6/26'),
                       ('20260601','20260608','6/1→6/8'),('20260608','20260626','6/8→6/26'),('20260506','20260626','全区间')]:
        if f'close_{a}' in r and f'close_{b}' in r:
            c=r[f'close_{a}']; c2=r[f'close_{b}']
            if c>0: r[f'chg_{lbl}']=round((c2-c)/c*100,1)
    results.append(r)

rdf=pd.DataFrame(results)
rdf.to_csv(f'{OUT}/analysis_summary.csv',index=False,encoding='utf-8-sig')
print('=== 全区间涨幅排名（5/6 → 6/26）===')
rdf_sorted=rdf.sort_values('chg_全区间',ascending=False)
for _,r in rdf_sorted.iterrows():
    print(f"  {r['name']:10s}  {r['code']:12s}  全区间 {r.get('chg_全区间','N/A')}%  6月低点反弹 {r.get('chg_6/8→6/26','N/A')}%")

# 材料股聚焦
print('\n=== 材料股聚焦 ===')
material=[r for _,r in rdf_sorted.iterrows() if r['name'] in ['沪硅产业','安集科技','雅克科技','鼎龙股份','江丰电子','艾森股份','飞凯材料','晶瑞股份']]
for r in material:
    print(f"  {r['name']:10s}  {r['code']:12s}  全区间 {r.get('chg_全区间','N/A')}%  6/8→6/26 {r.get('chg_6/8→6/26','N/A')}%")
