# 量化学习任务工作空间

量化交易学习与实践的工作空间，记录从数据获取、策略分析到回测的完整学习过程。

## 📁 目录结构

```
quant-learning/
├── README.md
├── .gitignore
├── data/                              # 原始与处理后的数据
│   └── huagong_000988_daily.csv       # 华工科技日线数据(241 个交易日)
├── figures/                           # 可视化图表
│   └── huagong_000988_close_price.png # 收盘价走势图
├── strategies/                        # 量化策略(待补充)
├── notebooks/                         # Jupyter 实验(待补充)
└── .workbuddy/                        # WorkBuddy 项目记忆
```

## 🚀 已完成的任务

- ✅ 配置 Anaconda + Tushare 数据源
- ✅ 获取华工科技（000988.SZ）过去一年日线数据
- ✅ 绘制每日收盘价曲线图
- ✅ 存储为 CSV 以备后续策略使用
- ✅ 推送到 GitHub

## 🛠️ 技术栈

- **Python 3.9** (Anaconda)
- **Tushare** — A 股金融数据
- **Pandas** — 数据处理
- **Matplotlib** — 可视化
- **Git + GitHub** — 版本管理

## 📊 数据来源

- 股票数据：[Tushare Pro](https://tushare.pro/)

## 📝 学习笔记

- 量化交易相比传统手工交易：速度快、无情绪、可回测、纪律性强
- K线：单个时间周期内 OHLC 价格的可视化
- 基本面：盈利能力、估值、成长性、财务健康
- 技术面：趋势指标、动能指标、量价分析、形态识别
