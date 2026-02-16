# Phase 2: Visual Perception - 完成情况

## 状态：已完成

## 目标

视觉感知层 — 模板匹配、OCR 文字识别、网格标注、统一元素检测、场景分类、弹窗过滤。

## 环境信息

| 项目 | 值 |
|------|-----|
| Python 版本 | 3.14.2 |
| OCR 引擎 | RapidOCR (ONNX Runtime) |
| 模板匹配 | OpenCV `TM_CCOEFF_NORMED` |
| 网格规格 | 8 列 x 6 行 (A1-H6) |
| 匹配阈值 | 0.8 |
| 新增依赖 | `rapidocr-onnxruntime` |

**注意：** 设计文档原定使用 PaddleOCR，但 PaddlePaddle 不支持 Python 3.14。改用 RapidOCR，底层使用相同的 PaddleOCR 模型（通过 ONNX Runtime 推理），API 兼容，效果一致。

## 已创建文件

```
SLGrobot/
  phase2.md                         # 本文档
  test_vision.py                    # Phase 2 测试脚本 (6 项测试)
  vision/
    template_matcher.py             # 模板匹配引擎
    ocr_locator.py                  # OCR 文字检测与定位
    grid_overlay.py                 # 网格标注 (用于 LLM 通信)
    element_detector.py             # 统一元素检测入口
  scene/
    __init__.py                     # 包导出
    classifier.py                   # 场景分类器
    popup_filter.py                 # 弹窗检测与自动关闭
```

## 已修改文件

| 文件 | 变更 |
|------|------|
| `vision/__init__.py` | 添加所有新模块导出 |
| `requirements.txt` | 添加 `rapidocr-onnxruntime` |

## 各模块说明

### `vision/template_matcher.py` — TemplateMatcher

基于 OpenCV `matchTemplate` 的模板匹配引擎：

- `__init__(template_dir, threshold)` — 启动时扫描 `templates/` 目录，将所有 PNG/JPG 加载到内存缓存。模板名为相对路径去掉扩展名，如 `buttons/close`
- `match_one(screenshot, template_name)` → `MatchResult | None` — 匹配单个模板，低于阈值返回 None
- `match_all(screenshot, category)` → `list[MatchResult]` — 匹配所有模板，可按类别过滤（如 `"buttons"`），按置信度降序排列
- `match_best(screenshot, template_names)` → `MatchResult | None` — 在指定列表中找最佳匹配
- `match_one_multi(screenshot, template_name, max_matches)` → `list[MatchResult]` — 查找同一模板的多个实例（非最大值抑制）
- `reload()` — 重新加载磁盘上的模板
- `get_template_names()` — 返回所有已加载模板名

数据类 `MatchResult`：`template_name`, `confidence`, `x`, `y` (中心坐标), `bbox` (x1, y1, x2, y2)

### `vision/ocr_locator.py` — OCRLocator

基于 RapidOCR 的文字检测与定位：

- `__init__()` — 延迟加载：首次调用时初始化 OCR 引擎，避免启动慢
- `find_text(screenshot, target_text)` → `OCRResult | None` — 查找特定文本（子串匹配，不区分大小写），返回最高置信度的匹配
- `find_all_text(screenshot)` → `list[OCRResult]` — 提取截图中所有文字及位置
- `find_numbers_in_region(screenshot, region)` → `str` — 从指定区域提取数字文本（用于资源栏读数），支持 `12,345`、`1.2M`、`500K` 等格式

数据类 `OCRResult`：`text`, `confidence`, `bbox` (x1, y1, x2, y2), `center` (cx, cy)

### `vision/grid_overlay.py` — GridOverlay

8x6 标签网格，用于 LLM 通信时的坐标语义化：

- `annotate(screenshot)` → `np.ndarray` — 在截图上绘制绿色网格线和单元格标签（A1-H6），黑底白字提高可读性
- `cell_to_pixel(cell)` → `(x, y)` — 网格标签转像素中心坐标，如 `"D3"` → `(472, 800)`
- `pixel_to_cell(x, y)` → `str` — 像素坐标转网格标签
- `get_cell_region(cell)` → `(x1, y1, x2, y2)` — 获取单元格边界框
- `get_all_cells()` → `list[str]` — 返回所有 48 个单元格标签

网格规格（1080x1920 屏幕）：每个单元格 135x320 像素，A1 在左上角，H6 在右下角。

### `vision/element_detector.py` — ElementDetector

统一元素检测入口，按优先级分发：

1. **模板匹配**（最快、最可靠，适用于已知元素）
2. **OCR 文字搜索**（适用于文本按钮/标签）
3. **轮廓检测**（基于 Canny 边缘 + 矩形过滤，作为后备）
4. **网格回退**（将目标解析为网格标签，返回单元格中心）

- `locate(screenshot, target, methods)` → `Element | None` — 查找 UI 元素，可指定检测方法列表覆盖默认优先级
- `locate_all(screenshot)` → `list[Element]` — 检测截图中所有可识别元素（合并模板 + OCR 结果）

数据类 `Element`：`name`, `source` ("template"|"ocr"|"contour"|"grid"), `confidence`, `x`, `y`, `bbox`

### `scene/classifier.py` — SceneClassifier

场景分类器，将截图分类为 6 种场景：

| 场景 | 说明 |
|------|------|
| `main_city` | 主城/基地界面 |
| `world_map` | 世界地图 |
| `battle` | 战斗或战斗结果 |
| `popup` | 弹窗/对话框覆盖 |
| `loading` | 加载/过渡画面 |
| `unknown` | 无法识别 |

检测方法组合：
- **模板匹配**：场景特征模板（`scenes/` 目录下的模板）
- **弹窗检测**：边缘暗度分析 — 弹窗使背景变暗，中心比边缘亮
- **加载画面检测**：灰度标准差低（颜色均匀）或亮度极端
- **主城启发式**：顶部资源栏饱和度检测
- **世界地图启发式**：绿色/棕色区域占比分析

- `classify(screenshot)` → `str` — 返回得分最高的场景名
- `get_confidence(screenshot)` → `dict[str, float]` — 返回所有场景的置信度

### `scene/popup_filter.py` — PopupFilter

弹窗自动检测与关闭，三级策略级联：

1. **模板关闭按钮**：搜索 `buttons/close`、`buttons/x`、`buttons/cancel`、`buttons/confirm`、`buttons/ok` 模板 → 点击
2. **任意按钮**：在弹窗区域搜索所有按钮模板，优先右上角（典型 X 按钮位置）→ 点击
3. **点击外部**：检测到暗色覆盖但找不到按钮时，点击边角区域关闭

- `is_popup(screenshot)` → `bool` — 检测是否有弹窗
- `handle(screenshot)` → `bool` — 检测并关闭弹窗，返回是否处理成功

## 测试结果

`python test_vision.py` — 6 项测试全部通过：

```
Test 1: Template Matcher .............. PASSED
  - 模板加载正常（当前 0 个模板，需要添加模板图片）
  - match_all 空模板返回空列表

Test 2: OCR Locator ................... PASSED
  - RapidOCR 初始化成功
  - 检测到 30 个文字区域
  - 包括: dX/dY/Xv/Yv 坐标、Prs 压力值、时间、数字等
  - find_numbers_in_region 正确提取数字

Test 3: Grid Overlay .................. PASSED
  - 8x6 网格，单元格 135x320 像素
  - A1→(67,160), D3→(472,800), H6→(1012,1760)
  - cell_to_pixel ↔ pixel_to_cell 双向转换正确
  - 标注图像已保存到 logs/grid_overlay_test.png

Test 4: Element Detector .............. PASSED
  - locate_all 找到 30 个元素（全部来自 OCR）
  - 网格回退正常：locate("D3", methods=["grid"]) 返回 (472, 800)

Test 5: Scene Classifier .............. PASSED
  - 当前截图分类为 main_city (score=0.300)
  - 所有场景均有置信度评分

Test 6: Popup Filter .................. PASSED
  - 当前截图正确识别为非弹窗
```

## 架构关系

```
ElementDetector (统一入口)
  ├── TemplateMatcher  ←── templates/ 目录中的 PNG 图片
  ├── OCRLocator       ←── RapidOCR (ONNX Runtime)
  └── GridOverlay      ←── config.py (GRID_COLS, GRID_ROWS)

SceneClassifier
  └── TemplateMatcher  ←── templates/scenes/ 目录

PopupFilter
  ├── TemplateMatcher  ←── templates/buttons/ 目录
  └── ADBController    ←── 点击关闭弹窗
```

## 待完善项

1. **添加模板图片** — 从游戏截图中裁剪关键元素，放入对应目录：
   - `templates/buttons/` — 关闭按钮(X)、确认、取消、OK
   - `templates/scenes/` — 各场景特征图片（主城资源栏、世界地图坐标框等）
   - `templates/icons/` — 常用图标（红点、加速、金币等）
2. **场景分类精度** — 当前仅使用启发式规则（得分较低），添加场景模板后精度将大幅提升
3. **OCR 精度调优** — 可针对游戏字体/配色调整预处理（二值化、对比度增强）

## 下一步: Phase 3

状态与战术决策层 — 游戏状态追踪、JSON 持久化、任务队列、规则引擎、自动处理器。
