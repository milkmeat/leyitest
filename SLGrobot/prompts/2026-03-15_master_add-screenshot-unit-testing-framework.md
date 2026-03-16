# Prompt Record

- Date: 2026-03-15 22:00
- Branch: master
- Commit: add screenshot unit testing framework for offline DOM regression

---

### 1. Implement screenshot testing framework

Implement the following plan:

# Screenshot Unit Testing Framework

## Context

The auto loop (screenshot → DOM → scene → action) is the core pipeline of SLGrobot but has no regression tests. DOM parsing and scene inference changes can silently break behavior. We need a framework that:
- Validates DOM parsing produces correct elements from known screenshots
- Validates scene inference is correct
- Validates AutoHandler produces the right tap action
- Runs offline (no emulator/ADB needed) from saved PNG files
- Supports per-game test data with easy case creation via a Claude Code skill

## Directory Structure

```
tests/
  __init__.py                     # empty
  screenshots/
    westgame2/
      main_city_001.png           # git-lfs tracked
      main_city_001.yaml          # expected output
    frozenisland/
      ...
  test_screenshot.py              # CLI regression runner
  screenshot_helpers.py           # pipeline init + assertion logic
  generate_expected.py            # draft YAML generator for new cases
.gitattributes                    # git lfs rule (create or append)
.claude/skills/add-screenshot-test.md  # Claude Code skill
```

**Files:** `tests/screenshot_helpers.py`, `tests/test_screenshot.py`, `tests/generate_expected.py`, `tests/__init__.py`, `.gitattributes`, `.claude/skills/add-screenshot-test.md`

### 2. Write usage docs in Chinese

把使用说明记录到文档，使用中文

**Files:** `docs/screenshot_testing.md`

### 3. Update progress.md

更新progress.md

**Files:** `progress.md`
