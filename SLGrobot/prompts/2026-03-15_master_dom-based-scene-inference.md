# Prompt Record

- Date: 2026-03-15 09:53
- Branch: master
- Commit: replace SceneClassifier with DOM-based scene inference in auto loop

---

### 1. Implement DOM-based scene inference plan

Implement the following plan:

# DOM-Based Scene Inference — Replace SceneClassifier

## Context

Currently the auto loop runs `SceneClassifier.classify(screenshot)` **before** DOM building, then injects the result into `dom["screen"]["scene"]`. This is redundant — `ScreenDOMBuilder.build()` already matches ALL templates and detects popups. The classifier re-does template matching and popup analysis that DOM already performed. This change moves scene inference **after** DOM building, deriving the scene from DOM elements that are already computed.

## Files to Modify

| File | Action | Purpose |
|------|--------|---------|
| `vision/screen_dom.py` | **Edit** | Add `infer_scene()` function, call it in `build()` |
| `main.py` | **Edit** | Remove classifier from auto_loop, use DOM scene directly |
| `scene/classifier.py` | **Keep** | Retain for `cmd_scene` CLI command (detailed confidence scores) |

**Files:** `vision/screen_dom.py`, `main.py`

### 2. Run auto loop test

python main.py auto --loops 5

### 3. Fix cmd_auto --loops parsing error

python main.py auto --loops 5

**Files:** `main.py`
