# Prompt Record

- Date: 2026-03-15 15:30
- Branch: master
- Commit: add building_upgrade_002 test and support both upgrade panel layouts

---

### 1. Add screenshot test

add screenshot test

**Files:** `tests/screenshots/westgame2/building_upgrade_002.png`, `tests/screenshots/westgame2/building_upgrade_002.yaml`, `vision/screen_dom.py`

### 2. Broaden building_upgrade detection

> **Q:** 升级按钮位置 (546, 1828) 不符合当前 building_upgrade 检测规则 (x>700, 800<y<1050)。需要放宽检测条件来覆盖这种底部升级面板吗？

放宽条件 (Recommended)

**Files:** `vision/screen_dom.py`

### 3. Correct detection constraints

升级按钮不一定是蓝色的，有时也是灰色。把位置检测加回去，这两种位置都有可能，都是building upgrade

**Files:** `vision/screen_dom.py`
