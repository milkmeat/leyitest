# Prompt Record

- Date: 2026-05-23 14:00
- Branch: master
- Commit: feat: AVA 对战结果 CSV → HTML 可视化工具

---

### 1

@ava_results.csv 已经有一场对战的记录了(可能会有多场)。写一个python程序，把它转化成一个html文件可视化，每一场对战画一个图，横轴是时间，纵轴是分数，每一方的得分是一条随时间变化的曲线。每次factory_capture事件发生时，在胜方的曲线上打一个标记。用文字总结：比分交换领先的次数，factory易手的次数，最后一次比分领先的时间占全长的百分比

> **Insight**
> - Chart.js 混合图表（line + scatter）共享同一个 category x 轴时，scatter 数据点的 x 值需要用标签数组的索引而非原始数值
> - `compute_summary` 用滑动窗口累计领先时间：遍历事件流，每两个事件之间根据上一个 leader 判断谁在累积领先时长
> - Factory 标记方向（→A / →B）通过 detail 字段中 "-> A" / "-> B" 文本匹配判定

**Files:** `visualize_ava.py`

### 2

横轴是时间(elapsed_sec),只需要有红蓝两条线(scorea,score_b)，factory_capture事件是标记在胜方线上面的一个星号。

> **Insight**
> - Chart.js 支持 per-point 配置：`pointRadius` 和 `pointStyle` 可以传数组，每个元素对应一个数据点，这样只有 factory 事件的点显示为星号，其余点隐藏（radius=0）
> - 这比用独立 scatter dataset 更干净，因为标记直接附着在曲线上，tooltip 也更自然

**Files:** `visualize_ava.py`
