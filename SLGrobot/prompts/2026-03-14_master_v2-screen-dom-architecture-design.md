# Prompt Record

- Date: 2026-03-14 23:00
- Branch: master
- Commit: add v2 Screen DOM architecture design and progress tracker

---

### 1. Propose Screen DOM refactoring vision

我想进行一次较大重构，改变现在的识图流程（detect_finger, detect_close_x, scene_classify, find_button, find_text等等）。新的思路为：

1. 截图当前画面，使用OCR，CV等python模块，识别屏幕上的可交互元素，将其转化成格式化的文本信息（不使用LLM），即当前画面描述
    1. 可交互元素包括文字、图标（每个游戏提供对应的图标库）、按钮
    2. 使用OCR识别所有可见文字，及位置
    3. 使用detect_finger类似的技术识别所有可见图标，及位置
    4. 使用边缘检测技术识别所有button，并关联OCR结果识别按钮文字、颜色
    5. 使用颜色检测技术识别 绿勾、红点 等未完成事件标志及位置
    6. 返回为类似html dom tree一样的结构化文字，描述当前画面上所有的可交互元素
2. 任务推理：使用LLM依据当前任务、历史画面描述与点击、当前画面描述（类dom tree），推断出应执行的点击、拖拽动作
3. 可以由LLM将某任务完成所需的一系列动作保存成脚本（基于画面描述的点击动作），不依赖LLM反复执行

先不要开发，向我提出问题澄清需求，完成方案设计

**Files:** `design_v2_screen_dom.md`

### 2. Clarify design requirements (10 questions)

> **Q:** 10 clarifying questions about DOM format, template matching scope, button definition, LLM call frequency, history context, LLM output format, script vs quest_scripts relationship, script abstraction level, migration strategy, and performance budget.

 1. 方案B，使用yaml格式
  2. 载入所有模板，约有50个
  3. 按钮：有明确的矩形边框，较鲜明的颜色，一般有可见文字
  4. 项目本身不调用llm。仅使用llm（claude code）为某项任务生成脚本，项目可以脱离llm执行脚本
  5. 就像日常对话一样，在claude code的会话中保存历史描述的信息，最多不超过10步
  6. 方案2。在执行脚本过程中，如果元素位置有小的变化，但dom tree结构不变，仍可执行
  7. 替代quest script
  8. 优先坐标，画面无变化时fallback 元素引用
  9. 在当前版本上做一个branch快照。新分支上全部重构。如果需要旧版本就切回老分支
  10. llm生成脚本的循环可以任意长。脱离llm直接运行脚本时每一步应<3s

**Files:** `design_v2_screen_dom.md`

### 3. Clarify follow-up questions (4 items)

> **Q:** 4 follow-up questions: OCR language, popup detection method, script conditional branching, and auto mode behavior.

1. 只需要中文+英文
2. 用半透明遮罩检测（颜色+面积）
3. 需要支持if
4. auto模式下，脱离llm运行，但也无法生成固定脚本，大致逻辑为
    1. 识别当前屏幕上的所有可交互元素，生成dom
    2. 根据dom的特征识别当前scene
    3. 不同scene下，可交互元素��优先级的，按当前scene的配置依次点击
        1. 未配置的scene优先点击手指，无手指的情况下点击其他元素（顺序待定）

**Files:** `design_v2_screen_dom.md`

### 4. Create v1 tag and branch

打v1标签，并建立v1分支。我们还是在main分支上进行v2开发

### 5. Push to remote

推送标签和分支到远端，先别做其他

### 6. Generate progress tracker

生成一个progress.md文档，详细说明
1. 每个phase的完成目标
2. 每个phase下面的详细todo清单，以后可以随进度更新
3. 每个phase的验收标准

**Files:** `progress.md`
