# Prompt Record

- Date: 2026-03-16 20:30
- Branch: master
- Commit: feat: add per-game template_match_threshold + frozenisland main_city_001 test

---

### 1. Implement per-game threshold plan

Implement the following plan:

# Plan: Add per-game template_match_threshold + frozenisland screenshot test

## Context

Adding a screenshot test case for frozenisland `main_city` scene. The test fails because:
- `world` icon template: half-res CCOEFF score is 0.6314 (< 0.7 threshold) → scene classified as `unknown`
- `tutorial_finger`: NCC scores ~0.58-0.64 (< 0.68 threshold) → finger not detected

The user wants **per-game thresholds** for frozenisland only (westgame2 unchanged).

## Changes

### 1. Add `template_match_threshold` to GameProfile
**File: `game_profile.py`**
- Add field: `template_match_threshold: float = 0.0` (0.0 = use class default)
- Load from JSON in `load_game_profile()`: `template_match_threshold=data.get("template_match_threshold", 0.0)`

### 2. Pass threshold when constructing TemplateMatcher
**File: `tests/screenshot_helpers.py` (line 55)**
- Change: `tm = TemplateMatcher(profile.template_dir)` →
  `tm = TemplateMatcher(profile.template_dir, profile.template_match_threshold or None)`

**File: `main.py` (line 116)**
- Change: `self.template_matcher = TemplateMatcher(template_dir)` →
  `threshold = game_profile.template_match_threshold if game_profile else None`
  `self.template_matcher = TemplateMatcher(template_dir, threshold or None)`

### 3. Update frozenisland game.json thresholds
**File: `games/frozenisland/game.json`**
- Add: `"template_match_threshold": 0.6`
- Change: `"finger_ncc_threshold": 0.68` → `"finger_ncc_threshold": 0.55`

### 4. Update test YAML
**File: `tests/screenshots/frozenisland/main_city_001.yaml`** (already created)
- scene: `main_city`
- required_elements: `close_x`, `task_scroll`, `tutorial_finger`
- auto_action: tap with `tutorial_finger` reason_match

## Verification

1. `python tests/test_screenshot.py frozenisland/main_city_001` — should pass
2. `python tests/test_screenshot.py` — full regression, all existing cases still pass

> **Plan**
> The plan above was provided by the user based on a prior planning session. During implementation, three additional issues surfaced beyond the plan:
> 1. `down_triangle` false positive (conf=0.63) at threshold 0.6 caused scene misclassification as `story_dialogue` — fixed by adding confidence floor (>= 0.75) in `infer_scene`
> 2. `tutorial_finger` passed NCC (stage 2) but failed boundary contrast (stage 3) — added `finger_boundary_threshold: 12.0` to game.json
> 3. YAML test used wrong element type (`icon`/`tutorial_finger`) instead of `finger` — corrected to match actual DOM structure

> **Insight**
> - per-game threshold 设计：`TemplateMatcher` 已有 `threshold` 参数，通过 `GameProfile` 中 `0.0` 哨兵值和 `or None` 实现 fallback 到类默认值
> - scene 分类与置信度：原来 `infer_scene` 只看 icon 名字是否存在，引入 `icon_max_conf` 追踪每个 icon 最高置信度，对 `story_dialogue` 要求 >= 0.75 消除假阳性
> - finger 三级过滤平衡：NCC 0.55 + boundary 12.0 精细调优，让真阳性 (boundary=12.8) 通过，过滤假阳性 (boundary=10.3)

**Files:** `game_profile.py`, `games/frozenisland/game.json`, `main.py`, `tests/screenshot_helpers.py`, `vision/screen_dom.py`, `tests/screenshots/frozenisland/main_city_001.yaml`

### 2. Simplify YAML test case

我把yaml里面不必要的require去掉了

**Files:** `tests/screenshots/frozenisland/main_city_001.yaml`

### 3. Align reason_match format

> **Q:** 这个reason_match的写法为什么和hero_upgrade_001.yaml不一样

> **Insight**
> - `_build_reason` 的格式规则：reason 字符串按 `priority:{action}:{type}:{detail}` 格式生成，finger 类型生成 `priority:tap_fingertip:finger`
> - `reason_match` 是正则匹配：`fingertip` 作为子串也能匹配，但规范写法 `"tap_fingertip:finger"` 更精确

**Files:** `tests/screenshots/frozenisland/main_city_001.yaml`

### 4. Configure git LFS

配置一下 git lfs
