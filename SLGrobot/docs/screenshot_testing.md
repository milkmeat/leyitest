# 截图单元测试框架

离线回归测试框架，用于验证 DOM 解析、场景推断和 AutoHandler 的正确性。无需模拟器/ADB，基于保存的 PNG 截图运行。

## 目录结构

```
tests/
  screenshot_helpers.py           # 核心模块：流水线构建 + 断言逻辑
  test_screenshot.py              # CLI 回归测试入口
  generate_expected.py            # 预期输出 YAML 草稿生成器
  screenshots/
    westgame2/
      main_city_001.png           # 截图（Git LFS 管理）
      main_city_001.yaml          # 预期输出
    frozenisland/
      ...
```

## 快速开始

### 1. 创建测试用例

**方式一：使用 Claude Code 技能**

在 Claude Code 中执行 `/add-screenshot-test`，会自动完成截图、生成 YAML、保存和验证的全流程。

**方式二：手动创建**

```bash
# 截图
python main.py screenshot test_capture

# 生成预期输出草稿（输出到终端）
python tests/generate_expected.py data/test_capture.png --game westgame2

# 检查输出，编辑后保存
cp data/test_capture.png tests/screenshots/westgame2/main_city_001.png
# 将 YAML 保存到 tests/screenshots/westgame2/main_city_001.yaml
```

### 2. 运行测试

```bash
# 运行所有游戏的所有用例
python tests/test_screenshot.py

# 只运行某个游戏的用例
python tests/test_screenshot.py westgame2

# 运行单个用例
python tests/test_screenshot.py westgame2/main_city_001
```

输出示例：

```
Found 3 test case(s)

--- westgame2 ---
  Pipeline init: 1.2s
  PASS  main_city_001 (2.3s)
  PASS  popup_001 (1.8s)
  FAIL  loading_001 (0.5s)
        Scene mismatch: expected 'loading', got 'unknown'

========================================
Total: 3  Passed: 2  Failed: 1
```

失败时退出码为 1，可集成到 CI。

## YAML 规范

每个 `<name>.yaml` 与同名 `<name>.png` 配对，格式如下：

```yaml
scene: main_city                   # 预期场景（精确匹配）

required_elements:                 # 必须存在的元素
  - type: icon
    name: world                    # name 精确匹配
  - type: button
    text_match: "领取"             # text 正则匹配
  - type: red_dot                  # 仅匹配类型
  - type: text
    value_match: "Lv\\.\\d+"      # value 正则匹配
  - type: button
    color_match: "green"           # color 正则匹配

forbidden_elements:                # 可选，不得出现的元素
  - type: icon
    name: territory

auto_action:                       # AutoHandler 预期输出
  type: tap                        # action type 精确匹配
  reason_match: "priority:tap:button:领取"  # reason 正则匹配
  # x: 540                        # 可选，默认容差 50px
  # y: 960
  # tolerance: 50                  # 自定义容差
```

### 特殊值

| `auto_action` 值 | 含义 |
|---|---|
| `null` | 期望 `get_action()` 返回 `None`（如 loading 画面） |
| 省略该字段 | 跳过 action 验证 |
| `{type: tap, ...}` | 验证 action 的 type、reason、坐标 |

### 元素匹配属性

| 属性 | 匹配方式 | 适用类型 |
|---|---|---|
| `type` | 精确匹配（必填） | 所有 |
| `name` | 精确匹配 | icon |
| `text_match` | 正则 | button |
| `value_match` | 正则 | text |
| `color_match` | 正则 | button |

## generate_expected.py 详解

```bash
python tests/generate_expected.py <png路径> [--game <游戏ID>]
```

- 默认游戏为 `westgame2`
- 对截图运行完整 DOM 流水线
- 自动提取所有 icon 和 button 作为 `required_elements`
- 自动填充 `auto_action`（包括 reason 的转义正则）
- 输出 YAML 到终端，供人工审查和编辑后保存

## 注意事项

- PNG 文件由 Git LFS 管理（`.gitattributes` 已配置）
- 每个游戏的流水线会缓存复用，避免重复初始化
- 测试按游戏分组执行，同一游戏的用例共享流水线实例
- `generate_expected.py` 生成的是**草稿**，应人工检查后再保存，特别是：
  - 去掉不稳定的元素（如随机出现的红点）
  - 调整过于严格的正则匹配
  - 添加 `forbidden_elements` 约束
