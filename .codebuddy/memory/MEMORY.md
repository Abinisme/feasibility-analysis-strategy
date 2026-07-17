# 长期记忆

## 技术配置
- Node.js + npm 已安装
- Python 3.14.5 (`/usr/local/bin/python3`)
- Tushare Token: `09b30bfc56d9d23bd624fe8373df8490c37e848aa749da28154c9543`
- 可用 Tushare 接口：daily(1/min), daily_basic(1/小时!), stock_basic, trade_cal, pro_bar
- 无权限接口：fina_indicator, income, moneyflow, moneyflow_hsgt, sw_daily, balancesheet, fund_daily（需2000+积分）
- hk_hold（沪深股通持股）现已 1次/小时 限频，且 fields 参数疑似不生效 → 北向结构化数据难抓
- Tushare 港股 daily(如0700.HK)常返回空 → 港股行情改用 Yahoo Finance web_fetch
- **NeoData 金融搜索技能**（neodata-financial-search）：金融数据查询优先用此技能（scripts/query.py，token 经 connect_cloud_service → $NEODATA_TOKEN）
  - 可返回：个股行情/历史走势（含区间涨跌幅，前复权）、板块、财报、资讯；北向资金排名类查询多返回 doc 资讯而非结构化表
  - token 偶发 401，按技能规则仅重试 1 次（重连 connect_cloud_service），仍失败则停止
  - 2026-07-10 实测：北向Q2持股披露原文由 NeoData 抓到（上海证券报/财联社），含总持仓3.13万亿、前十名单、行业前三；个股Q2区间涨跌幅用「股票历史走势」意图可批量获取

## 报告更新工作流（feasibility-analysis-strategy 项目）
- 项目含多个 HTML 报告（腾讯/比亚迪/半导体/人形机器人/核聚变等），统一深色主题风格
- 数据更新流程：Tushare 拉A股 → Yahoo 拉港股/美股 → 全篇交叉引用同步（meta/估值表/箱体/K线/综合研判/页脚）
- K线图用 Lightweight Charts v4，月线数据；当前价线应显示实际最新收盘价（非lastClose）
- 提交规范：`git add -A && git commit -m "feat/fix: ..." && git push origin main`

## 半导体分析项目
- 脚本位置：`scripts/fetch_quick.py`（快速数据抓取）、`scripts/generate_report.py`（报告生成）
- 数据位置：`data/batch1_quotes.csv`（个股日K线+ETF+指数）
- 报告输出：`semiconductor_expansion_deep_dive_20260629.html`
- 标的池：18只个股（含6只材料股）+ 5ETF + 3指数

## Dreamina（即梦）CLI
- 安装：`curl -fsSL https://jimeng.jianying.com/cli | bash`
- 二进制：`~/.local/bin/dreamina`（x86_64）
- VIP等级 artisan（199/月），CLI需要 maestro VIP → 无法使用生成功能
