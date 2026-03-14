# Prompt Record

- Date: 2026-03-15 00:00
- Branch: master
- Commit: auto-detect game from emulator foreground app package

---

### 1. Auto-detect game from foreground app

增加一个功能：在模拟器上执行时，读取当前app的package判断是哪个游戏，并自动切换（相当于自动使用--game参数）。如果不在配置列表内就打印package名字，退出。

**Files:** `device/adb_controller.py`, `main.py`
