# 长期记忆

## 技术配置
- Node.js + npm 已安装
- Python 3.14.5 (`/usr/local/bin/python3`)
- Tushare Token: `09b30bfc56d9d23bd624fe8373df8490c37e848aa749da28154c9543`
- 可用 Tushare 接口：daily, daily_basic(1/min), stock_basic
- 无权限接口：fina_indicator, income, moneyflow, sw_daily, balancesheet, fund_daily（需2000+积分）

## 半导体分析项目
- 脚本位置：`scripts/fetch_quick.py`（快速数据抓取）、`scripts/generate_report.py`（报告生成）
- 数据位置：`data/batch1_quotes.csv`（个股日K线+ETF+指数）
- 报告输出：`semiconductor_expansion_deep_dive_20260629.html`
- 标的池：18只个股（含6只材料股）+ 5ETF + 3指数

## Dreamina（即梦）CLI
- 安装：`curl -fsSL https://jimeng.jianying.com/cli | bash`
- 二进制：`~/.local/bin/dreamina`（x86_64）
- VIP等级 artisan（199/月），CLI需要 maestro VIP → 无法使用生成功能
