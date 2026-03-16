# Prompt Record

- Date: 2026-03-15 16:33
- Branch: master
- Commit: add hero_recruit_001 test, fix scene detection and priority rules

---

### 1. Add screenshot test

add screenshot test

**Files:** `tests/screenshots/westgame2/hero_recruit_001.png`, `tests/screenshots/westgame2/hero_recruit_001.yaml`

### 2. Fix scene detection for hero_recruit

> **Q:** Scene detected as unknown (no hero_recruit icon template). Should I save as-is or fix scene detection?

Fix scene detection

### 3. Detection criterion is 英雄招募 text in top-right

> **Q:** This is the 英雄招募 screen. Scene detected as unknown. Should I save as unknown or fix detection?

英雄招募scene的识别标准是右上角有 英雄招募 文字（分了两行，我不确定是否会识别成两个元素）

**Files:** `vision/screen_dom.py`

### 4. Hero recruit priority rules

英雄招募场景的处理优先级是
1. 优先点击有 免费 文字的按钮
2. 都没有的话，点击 back arrow
3. back arrow也是必须元素

**Files:** `games/westgame2/game.json`, `tests/screenshots/westgame2/hero_recruit_001.yaml`

### 5. Match 免费 in reason

> **Q:** auto_action reason_match 是 "tap:button:招募1次"

这里是不是match 免费 更好一点

**Files:** `tests/screenshots/westgame2/hero_recruit_001.yaml`
