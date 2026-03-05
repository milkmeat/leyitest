# Prompt Record

- Date: 2026-03-05
- Branch: master
- Commit: regenerate train quest script from updated train.md

---

### 1

train.md更新了，重新生成quest script

> **Insight**
> - Quest script 的 `repeat` 字段让同一步骤执行 N 次，用于 `find_building` 时会重复定位+点击
> - MD 中 `[[xxx.png]]` 是模板引用语法，生成 JSON 时需要根据实际路径补全前缀（如 `icons/train_brawler`）
> - `find_building` 第二次执行时建筑已在屏幕上，定位很快，所以 `repeat: 2` 是安全的
> - `find_building` 加 `repeat: 2` 的原因：进入步兵营时，如果之前有训练完成的士兵，第一次点击会弹出"收集士兵"的界面，第二次点击才真正进入训练面板。这是 SLG 游戏中常见的"中间态拦截"模式。
> - `tap_text` 的 `-1` 索引表示点击 OCR 识别到的最后一个匹配文本，在多个同名按钮的界面中定位到底部/最新的那个。

**Files:** `games/westgame2/game.json`
