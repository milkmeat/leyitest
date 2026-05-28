# Prompt Record

- Date: 2026-05-28 00:00
- Branch: master
- Commit: fix: visualize_ava 折线图 x 轴改为线性均匀刻度（精确到分钟）

---

### 1

@visualize_ava.py 所生成的折线图，它的横坐标不是均匀的。把它改成均匀的刻度（精确到分钟）

> **Insight**
> - 原来的图表使用 `labels` 数组作为 x 轴，Chart.js 将其视为**分类轴**（categorical），每个数据点等距排列，无论实际时间间隔多大。
> - 改为 `type: 'linear'` 线性轴 + `{x, y}` 数据点格式后，x 轴按真实时间值等比例分布，刻度以 `stepSize: 1` 精确到每分钟一格。
> - 这样事件密集的时段数据点会聚拢，稀疏时段会留白，更真实地反映比赛节奏。

**Files:** `visualize_ava.py`
