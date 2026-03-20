# Prompt Record

- Date: 2026-03-20 18:30
- Branch: master
- Commit: feat: add --soldier param to l0 CLI and Smart L0 preprocessing

---

### 1. Implement l0 --soldier optional parameter plan

Implement the following plan:

# CLI l0 命令支持可选兵种/数量参数

## Context

`_build_march_info` 自动选择数量最多的兵种，出征 DEFAULT_MARCH_SIZE=5000。CLI 调试时需要手动指定兵种和数量。

## 修改文件

`src/executor/l0_executor.py` + `src/main.py`

## 工作项

### 1. AIInstruction 新增字段 (`l0_executor.py:79`)

```python
soldier_id: int = 0              # 手动指定兵种ID（0=自动选择）
soldier_count: int = 0           # 手动指定出征数量（0=默认）
```

### 2. `_build_march_info` 加参数 (`l0_executor.py:543`)

```python
def _build_march_info(self, uid: int, needs_hero: bool = True,
                      soldier_id: int = 0, soldier_count: int = 0):
```

- `soldier_id > 0` → 直接使用，跳过自动选择
- `soldier_count > 0` → 使用该值（仍受 DEFAULT_MARCH_SIZE 上限）

### 3. `_dispatch` 传递参数 (`l0_executor.py:341`)

唯一调用处改为：
```python
march = self._build_march_info(instr.uid, needs_hero=...,
                                soldier_id=instr.soldier_id, soldier_count=instr.soldier_count)
```

### 4. CLI shorthand 统一解析 `--soldier` (`main.py:_parse_l0_shorthand`)

在所有 action 分支之后、`return data` 之前，统一从原始 args 中提取 `--soldier <id> <count>`。

用法：
```bash
python -m src.main l0 LVL_ATTACK_BUILDING 20010644 10006_xxx 154 170 --soldier 204 3000
```

> **Insight**
> - `_build_march_info` 当前自动选数量最多的兵种，出征 DEFAULT_MARCH_SIZE=5000。新增参数允许 CLI 覆盖这个逻辑。
> - `--soldier` 放在 `_parse_l0_shorthand` 的统一位置（所有 action 分支之后），避免在每个分支中重复解析。
> - `_dispatch` 是唯一调用 `_build_march_info` 的地方，只需改一处。

> **Insight**
> - **参数隔离**: `--soldier` 在构建 `rest` 之前就被过滤掉了，这样无论放在命令行哪个位置都不会被误认为是位置参数（如 building_key 或 prepare_time）。
> - **向后兼容**: `soldier_id=0` 和 `soldier_count=0` 是默认值，不传 `--soldier` 时走原有的自动选兵逻辑，对 AI 决策路径（L1→L0）零影响。
> - **上限保护**: 即使手动指定 `soldier_count`，仍受 `DEFAULT_MARCH_SIZE=5000` 上限约束，防止测试时意外发送过大的出征请求。

**Files:** `src/executor/l0_executor.py`, `src/main.py`

### 2. Document new --soldier CLI usage

把新增的这些cli的命令与参数用法记录到文档

> **Insight**
> - 文档更新了两处：**模块 docstring**（开发者看代码时看到）和 **help 输出**（用户运行 `python -m src.main` 时看到），保持一致。
> - `--soldier` 作为所有 `l0` 子命令的通用选项记录，而非在每个 action 分支下重复——这与实现中"统一解析"的设计一致。

**Files:** `src/main.py`
