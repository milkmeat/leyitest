# Prompt Record

- Date: 2026-03-15 00:00
- Branch: master
- Commit: flatten template directories and remove unused templates

---

### 1. Flatten template directories and update code

我把两个游戏的games/<gamename>/templates/目录都做了清理。去除了无用的模板（以后应该可以用OCR覆盖），去掉了目录结构，只保留单层目录。请修改对应的代码和配置，保证程序能正常运行。

**Files:** `vision/template_matcher.py`, `scene/classifier.py`, `scene/popup_filter.py`, `brain/finger_detector.py`, `brain/quest_script.py`, `brain/auto_handler.py`, `brain/script_runner.py`, `vision/element_detector.py`, `vision/quest_bar_detector.py`, `main.py`, `games/frozenisland/game.json`, `games/westgame2/game.json`, `test_quest_script.py`, `CLAUDE.md`
