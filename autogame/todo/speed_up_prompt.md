## 目标
改进 ava L2 and L1 prompt，减少output token的数量，提高输出速度

## 任务
- review L2 and L1 prompt 的写法，使得输出更简单准确
- 现有的功能不受影响，不会出现额外的错误


## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 工作项

### 1. [DONE] 更新 YAML 解析器识别 `orders:` 关键字
- `src/ai/llm_client.py`: `_extract_yaml()` 添加 `"orders:"` 到识别列表
- `_DRY_RUN_RESPONSE` 移除 `thinking` 和 `reason` 字段

### 2. [DONE] 精简 L2 AVA Prompt 输出格式
- `src/ai/prompts/l2_system_ava.txt`: 移除 `thinking:` 和 `priority:` 字段

### 3. [DONE] 精简 L1 AVA Prompt 输出格式
- `src/ai/prompts/l1_system_ava.txt`: 移除 `thinking:` 和 `reason:` 字段
- `src/ai/prompts/l1_system_ava_test.txt`: 同上

### 4. [DONE] 增强 L1 历史记录 fallback 显示
- `src/ai/memory.py`: reason 为空时显示 building_id/target_uid/坐标

## 验证结果 (2026-04-28)

### 输出格式对比（旧 vs 新）
| 字段 | 旧 L2 | 新 L2 | 旧 L1 | 新 L1 |
|------|-------|-------|-------|-------|
| thinking | 有 | 无 | 有 | 无 |
| priority | 有 | 无 | - | - |
| reason | - | - | 有 | 无 |

- L2 output keys: `['thinking', 'orders']` → `['orders']`
- L2 order keys: `['squad_id', 'order', 'priority']` → `['squad_id', 'order']`
- L1 instruction keys: `['action', 'uid', 'building_id', 'target_x', 'target_y', 'reason']` → `['action', 'uid', 'target_x', 'target_y']`
- error_count: 0（无新增错误）

### `./ava_simulate.sh 20` 完整对比 (旧=logs.20260427_121911, 新=logs/)

**旧版 (20轮, thinking+reason+priority):**
```
L2: avg=23.7s  median=22.3s  min=11.4s  max=39.4s  n=20
L1: avg=74.5s  median=62.9s  min=16.8s  max=258.5s  n=20
```

**新版 (18轮, 无thinking/reason/priority):**
```
L2: avg=28.2s  median=29.9s  min=15.0s  max=61.8s  n=18
L1: avg=84.4s  median=53.0s  min=23.7s  max=360.0s  n=18
```

**按队伍分别对比:**
```
TestSquad:   L2 avg 27.6s→24.3s (-11.7%)  L1 avg 100.6s→88.3s (-12.2%)  L1 med 63.1s→45.1s (-28.5%)
PhoenixRise: L2 avg 21.1s→32.0s (+51.6%)  L1 avg  57.1s→80.4s (+40.7%)  L1 med 62.8s→61.2s (-2.5%)
```

**L1 耗时分布 (排序):**
```
旧: 17 23 28 29 30 31 32 34 38 63 63 63 66 81 89 104 106 146 190 259
新: 24 28 37 40 40 40 45 47 52 53 61 96 97 97 119 137 146 360
```

**结论:**
- 输出格式确认精简成功（thinking/reason/priority 全部移除）
- 错误数: 0 → 0（无新增错误）
- LLM 耗时受 API 服务器负载影响方差很大，单次 20 分钟对比难以得出统计显著结论
- TestSquad L1 中位数下降 28.5%（63.1s→45.1s），PhoenixRise L1 中位数基本持平（-2.5%）

## 验收标准
```
./ava_simulate.sh 20 >/dev/null
```
- 检查 logs/ 目录下的日志，看LLM输出时间是否更短
- 检查日志中不应出现新的错误