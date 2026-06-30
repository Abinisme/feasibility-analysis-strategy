#!/usr/bin/env python3
"""计算更新报告所需全部指标"""
import pandas as pd
df=pd.read_csv('data/batch1_quotes.csv')
df['trade_date']=df['trade_date'].astype(str)

codes=['688981.SH','688347.SH','002371.SZ','688012.SH','688072.SH',
       '688200.SH','688082.SH','688126.SH','688019.SH',
       '002409.SZ','300666.SZ','002312.SZ','688720.SH',
       '601133.SH','603859.SH','603998.SH']
names=['中芯国际','华虹半导体','北方华创','中微公司','拓荆科技',
       '华峰测控','盛美上海','沪硅产业','安集科技',
       '雅克科技','江丰电子','鼎龙股份','艾森股份',
       '柏诚股份','能科科技','方邦股份']

def p(code, date):
    r=df[(df['ts_code']==code)&(df['trade_date']==date)]
    return round(r.iloc[0].close,2) if len(r)>0 else None

def chg(c,a,b):
    pa,pb=p(c,a),p(c,b)
    if pa and pb and pa>0: return round((pb-pa)/pa*100,1)
    return None

for code,name in zip(codes,names):
    d626=p(code,'20260626')
    d608=p(code,'20260608') or p(code,'20260609')
    d601=p(code,'20260601')
    d506=p(code,'20260506')
    d515=p(code,'20260615')
    d529=p(code,'20260529')
    
    c56=chg(code,'20260506','20260626')
    c529=chg(code,'20260529','20260626')
    c601=chg(code,'20260601','20260626')
    c608=chg(code,'20260608','20260626') or chg(code,'20260609','20260626')
    c515=chg(code,'20260615','20260626')
    
    print(f'{name:8s} {code} 5/6:{d506} 5/29:{d529} 6/1:{d601} 6/8:{d608} 6/15:{d515} 6/26:{d626} | 56→26:{c56:+.1f}% 61→26:{c601:+.1f}% 608→26:{c608:+.1f}%')
