# auto_manim 提示词融合手册

面向 ManimGL + AutoScene 的统一提示词与规范，合并项目内所有提示词与硬性约束，直接粘贴即可用。

## 0. 快速索引

- AI-1（题目图片输入）：5.1
- AI-1（视频解析/洗稿）：5.3
- AI-1（PPT 解析/复刻）：5.4
- AI-2（ManimGL/AutoScene 代码生成）：5.5
- 排版/动态/字幕补丁：5.6
- 代码骨架与算法模板：6.x

## 1. AutoScene/ManimGL 能力速查

### 1.1 配音与字幕

- `speak(text, subtitle=None, color_map=None, min_duration=2.0) -> float`：自动配音+字幕（支持分离）
- `speak_with_highlight(text, targets=None, subtitle=None, color_map=None, min_duration=2.0) -> float`：配音+字幕+高亮
- `speak_sequence(texts, min_duration=2.0)`
- `run_timeline(events, generate_voice=None)`
- `make_subtitle(text, color_map=None) -> VGroup`：背景+文字，默认 fix_in_frame
- `subtitle(t0, t1, text, color_map=None)`：第1句 Write，后续 Transform
- `clear_subtitle(t=None)`
- `set_subtitle_style(font_size=None, edge_buff=None, max_chars=None)`
- `export_srt(events, path)`

### 1.2 视觉引导与标注

- `focus_guide` / `focus_guide_sequence`
- `focus_guide_with_camera` / `focus_guide_with_camera_sequence`
- `highlight_text(effect=box/underline/background/indicate/focus/wave/random)`
- `add_curved_annotation` / `add_multi_curved_annotations`
- `annotate_region`
- `get_text_part` / `get_text_parts`

### 1.3 相机与固定元素

- `camera_focus(target, zoom_factor=..., focus_time=..., hold_time=..., restore_time=...)`
- `add_fixed_title` / `add_fixed_subtitle` / `add_fixed_formula`
- `add_fixed_annotation` / `add_fixed_annotation_dynamic`
- `add_grid_background` / `add_traffic_lights`

### 1.4 辉光与脉动

- `create_glow_text` / `create_glow_tex`
- `add_glow_to_curve`
- `create_pulse_glow_curve` / `create_pulse_glow_function` / `create_pulse_glow_circle`

### 1.5 调试与时间

- `enable_debug` / `enable_time_hud`
- `mark` / `get_markers` / `get_current_time`

### 1.6 布局辅助

- `ensure_above_subtitle(mobject, viz_bottom_y=None, margin=0.3, overlap_buff=0.2)`

### 1.7 默认常量（可通过 set_subtitle_style 覆盖）

- `SUBTITLE_FONT="STKaiti"`
- `SUBTITLE_FONT_SIZE=28`
- `SUBTITLE_MAX_CHARS_PER_LINE=20`
- `VOICE_GAP_DURATION=0.5`

## 2. 工作流总览

- 核心流程：题目输入 → AI-1 产出结构化时间轴 JSON → 人工校对 → AI-2 生成 ManimGL/AutoScene 代码 → 渲染/剪辑
- AI-1 只负责结构化 JSON（旁白/时间戳/画面驱动字段）
- AI-2 只负责把 JSON 翻译成可运行代码（按时间轴执行）
- 输入来源：图片题 / 视频解析 / PPT 解析

## 3. 阶段独立性原则（Phase Independence）

### 3.1 问题背景

AutoScene 项目通常将动画拆分为多个 `phase_xxx` 方法（如 `phase1_intro`, `phase2_modeling` 等），各阶段通过 `shared_objects` 字典共享对象。但单独测试某一阶段时，若前序阶段未执行，访问共享对象会报错。

### 3.2 解决方案：安全共享对象访问

AutoScene 基类提供三个安全方法：

```python
# 1. 安全获取（支持延迟创建）
final_eq = self.get_shared("final_eq", factory=lambda: Tex(r"T(t)=20+10\cdot0.8^{t/2}"))

# 2. 设置共享对象
self.set_shared("title", title_text)

# 3. 安全淡出（忽略不存在的对象）
self.safe_fadeout("title", "problem", "chart")
```

### 3.3 代码规范

**每个 phase 必须自给自足：**

```python
def phase4_result(self):
    # ❌ 错误 - 直接访问可能为 None
    final_eq = self.shared_objects["final_eq"]
    
    # ✅ 正确 - 使用安全获取，提供 factory 创建缺失对象
    final_eq = self.get_shared("final_eq", factory=lambda: 
        Tex(r"T(t)=20+10\cdot0.8^{t/2}", font_size=28, color=GREEN)
    )
    
    # ❌ 错误 - 可能报错
    self.play(FadeOut(self.shared_objects["title"]))
    
    # ✅ 正确 - 安全淡出
    self.safe_fadeout("title", "underline", "problem")
```

### 3.4 测试方式

在 `construct()` 中注释掉其他阶段，单独测试任一阶段：

```python
def construct(self):
    self.setup_scene()
    # self.phase1_intro()
    # self.phase2_modeling()
    self.phase4_result()  # 单独测试此阶段
```

## 4. JSON Schema 与 visual_action 映射

### 4.1 最小 Schema

```json
{
  "meta": {"title":"竖版标题","resolution":"1080x1920","target_duration":[60,120]},
  "timeline":[
    {
      "scene_id":"S1","section":"intro",
      "start":0.0,"end":3.2,
      "narration":"今天我们用一个例子理解……",
      "screen_text":"一个例子理解XXX",
      "latex":"", "visual_action":"标题"
    }
  ],
  "total_duration":120.0
}
```

### 4.2 推荐 Schema（完整版）

```json
{
  "meta": {
    "title": "竖版标题",
    "resolution": "1080x1920",
    "target_duration": [60, 120],
    "style": {
      "font_cn": "STKaiti",
      "font_en": "Arial",
      "title_size": 48,
      "body_size": 36,
      "primary_color": "#FFFFFF",
      "accent_color": "#FF6B6B"
    }
  },
  "timeline": [
    {
      "scene_id": "S1",
      "section": "intro",
      "start": 0.0,
      "end": 3.2,
      "narration": "今天我们用一个例子理解……",
      "screen_text": "一个例子理解XXX",
      "latex": "",
      "visual_action": "标题",
      "objects": [
        {"id": "title_main", "type": "Text", "content": "一个例子理解XXX", "position": "UP", "style": "title"}
      ],
      "animations": [
        {"type": "Write", "target": "title_main", "run_time": 2.0, "rate_func": "smooth"}
      ]
    }
  ],
  "total_duration": 120.0
}
```

### 4.3 visual_action → 动画映射

| visual_action | 动画组合        | 常用 API                             |
| ------------- | --------------- | ------------------------------------ |
| 标题          | 写入 + 下划线   | `Write` + `Underline`            |
| 定义          | 写入 + 框选     | `Write` + `SurroundingRectangle` |
| 示意图        | 创建 + 高亮     | `ShowCreation` + `FlashAround`   |
| 推导          | 分行写入 + 变换 | `TransformMatchingTex` / `Write` |
| 例题          | 写入 + 框选     | `Write` + `SurroundingRectangle` |
| 强调          | 指示 + 闪烁     | `Indicate` / `FlashAround`       |
| 小结          | 渐入 + 列表     | `FadeIn` + `VGroup`              |
| 转场          | 淡出全部        | `FadeOut(*self.mobjects)`          |

## 5. 提示词库（可直接复制）

### 5.1 AI-1（题目图片输入）：一体化提示词（上下文 + OCR/抽取 + 结构化 JSON）

```markdown
你是短视频脚本与时间轴编排器。请基于我给出的题目图片（可含文字补充），生成「旁白 + 时间戳 + 画面驱动字段」的 JSON。

【输入信息（请填写）】
1) 图片类型：截图/照片/扫描件/拼接图
2) 题目来源：【高考真题·函数综合】/【竞赛·几何】等
3) 期望解法风格：考试版/讲解版/竞赛版
4) 目标时长：60s / 3min / 8min
5) 讲解深度：只讲关键步骤 / 讲完整推导

【规则】
1) 字速：intro 5 字/s，middle 4.5 字/s，outro 5 字/s；时间精度 0.1s，严格递增不重叠。
2) 停顿：句末 0.2–0.4s；转场 0.6–1.0s（单独事件，visual_action="转场"）。
3) 每句字段：scene_id，section(intro/middle/outro)，start，end，narration，screen_text，latex，visual_action（限定：标题/定义/示意图/推导/例题/强调/小结/转场）。
4) 总时长控制在 [60,90]s（如未指定以此为准）。
5) 图片题特有：先抽取题面关键信息并重排成“上屏版”；公式用可编译 LaTeX；不确定处用【?】标注，避免臆测。
6) 讲解与上屏分离：narration 用口语化 TTS 文案，screen_text 用更“数学化”的上屏文本；公式优先放在 latex 字段。
7) 一句一动作：每句只表达一个动作意图，visual_action 必须可驱动对应画面变化。

【输出】仅输出 JSON，不要解释。
附加上下文：<粘贴来源/时长/深度等>
题目图片：<粘贴图片>
补充文字：<可选>
```

**图片工作流快速步骤**

1) 发题目图片 + 上下文 → 用 5.1 提示词生成 JSON
2) 检查 JSON → 人工校对时间戳/公式/旁白
3) 发给 AI-2 → 生成 AutoScene 代码（见 5.5）
4) 运行调试 → `self.enable_debug(True)` 逐阶段检查
5) 渲染输出 → `manimgl script.py SceneName -w --resolution 1080x1920`

#### 5.1-增强：题目图片高精度解析与可复刻抽象（严格版）

```markdown
0) 输入约束（你提供图片时建议附带，但不是必须）
图片类型：截图/照片/扫描件/拼接图
若有：题目来源（章节/编号/课程）、期望解法风格（考试版/讲解版/竞赛版）
若有：目标时长（例如 60s / 3min / 8min），或目标讲解深度（只讲关键步骤/讲完整推导）

你必须输出的内容（逐项给出）
1) 题面信息抽取与可靠性标注（必须）
对图片做“结构化 OCR + 版面理解”，输出：
- 题目逐字稿（原题面）
- 分块输出：标题/题干/小问(1)(2)(3)/已知条件/图形标注/表格/注释
- 对每一块给出：
  - content：逐字文本（公式用可编译 LaTeX）
  - type：Text / MathTex / 纯符号 / 图形标注
  - confidence：高/中/低（低则必须给替代方案）
  - uncertain_spans：不确定片段用 【?】 标记

图形/示意图解析（若存在）
- 列出所有几何对象或示意元素：点、线段、角标、坐标轴、曲线、阴影区域、箭头、表格列标题等
- 若无法完全确定，必须写明：
  - 无法确定的原因（遮挡/像素/倾斜/光照）
  - 近似方案 A/B（例如：用简化示意图替代；或直接保留原图并框选关键区域）

版面布局摘要（用于复刻相对位置）
- 用“屏幕归一化坐标”描述每个块的位置（不要求像素级，但要可复刻）
- 建议格式：block_name: bbox=(x0,y0,x1,y1)，x,y ∈ [0,1]，以屏幕左下为 (0,0)

目标：保证“题目内容不会抄错/漏条件/漏符号”。如果某处低置信度，你必须在输出里显式标注并给两套可执行方案。

2) 可复刻的“题目重排版”版本（必须）
输出一份“适合上屏讲解”的重排版题面（不是照搬图片布局，而是板书/课件风格），要求：
- 标题（可选）：如“例题：xxx”
- 题干：按语义断行，避免一行过长
- 公式：全部给出可编译 LaTeX（MathTex）
- 小问：编号统一（(1)(2)(3) 或 a,b,c）
- 若原图有图：给出图的复刻版本或“保留原图 + 框选 + 标注”的替代策略

输出时必须同时提供：
- DisplayVersion：最终上屏文本/公式（可直接变成 Text/Tex/MathTex）
- SourceMapping：每一行对应原图哪个信息块（便于校对）

3) 分镜脚本（Shot List，带时间戳，必须）
将“题目图片 → 题面重排版 → 解题过程 → 总结”切分镜头，至少到 1s 精度。每个 Shot 必须包含：
- Shot 编号
- 时间范围（例如 00:00–00:06）
- 画面状态描述（对象有哪些、相对位置）
- 核心变化（出现/消失/变形/移动/高亮/框选/相机运动）
- 讲解意图（这一镜头讲什么，为什么需要这个变化）

推荐镜头模板（可按需要删改）：
- 开场：展示原题图片（或题面重排版标题）
- 题面信息聚焦：框选条件/问法/关键图形
- 题面净化：Transform 成清爽排版版本
- 解题主线：逐步推导（每步一个视觉“落点”）
- 结果汇总：框出最终答案 + 条件回扣（可选：检验/讨论）

4) 场景对象清单（Mobject 级别清单，必须）
以“可写成代码”的粒度列出对象，要求包含变量名建议、类型、样式、布局与复用关系：
- 全局对象（复用）：title、subtitle、watermark、page_frame、step_index、highlight_box 等
- 题面对象：
  - img_problem（ImageMobject，原题图，可选）
  - stmt_group（重排版题面 VGroup：Text/Tex/MathTex）
  - fig_group（几何/示意图对象集合，若有）
- 解题对象：
  - eq_1, eq_2, ...（每一步公式）
  - note_1, note_2, ...（解释性短句）
  - mark_assumption / mark_key（框选、下划线、箭头、颜色高亮）

每个对象必须给：
- 类型：Text/Tex/MathTex/Line/Arrow/SurroundingRectangle/Brace/Axes/NumberPlane/ImageMobject 等
- 样式：颜色（hex 或 Manim 常量）、stroke_width、fill_opacity、font、font_size、buff
- 布局：to_edge/next_to/align_to/shift/scale 的相对描述
- 复用说明：哪些对象只创建一次，哪些是 Transform 的目标

5) 动画事件时间轴（ManimGL 动作词 + 参数，必须）
按顺序列出可直接映射到 ManimGL 的事件。每条事件必须包含：
- 时间点（绝对秒或相对序号）
- 动作类型：ShowCreation / FadeIn / FadeOut / Write / Transform / ReplacementTransform / Indicate / Wiggle / Flash / ApplyMethod / MoveToTarget / Uncreate 等
- 参数：run_time、rate_func、lag_ratio、path_arc（如有）
- 并行动画：同一个 self.play(...) 里有哪些动画同时发生
- 与字幕同步：该事件对应哪句字幕（subtitle_id）

要求：
- 对“题面重排版”必须指定：TransformMatchingTex / ReplacementTransform / FadeTransformPieces 或简单 Fade。
- 对“推导链”必须说明：新公式是 Write 还是由旧公式 Transform 而来（减少跳变）。

6) 相机与构图（若需要，必须）
若你希望“框选题面细节/放大图形/推导区分屏”，则必须输出：
- 初始 camera frame：位置、缩放（scale 或 width/height 的相对说明）
- 每次镜头运动：起止时间、目标区域、缓动函数
- 推荐写法（ManimGL）：self.play(self.camera.frame.animate.scale(...).move_to(...), ...)
- 是否需要“跟随对象”：例如跟随当前推导行、或在图形局部放大

7) 字幕文稿与旁白稿要求（强制：用于你的工作流）
7.1 字幕清单格式（必须）
- 以表格或 YAML/JSON 形式输出，每条字幕包含：
  - id：S001, S002, ...
  - t_start：起始时间（mm:ss 或秒）
  - t_end：结束时间
  - text：一句话字幕（中文为主，允许夹公式）
  - mode：title / subtitle / narration / equation_hint
  - on_screen：是否同步上屏（true/false）
  - action_hint：建议动作
  - anchor：字幕摆放策略（bottom_center / top_left 等）
  - pace_note：语速说明（快/中/慢）
- 第一条：Write
- 后续：Transform 上一句 → 下一句

7.2 字幕时长生成规则（必须写明并执行）
- 开场字幕：5 字/秒（或等效英文 12–15 chars/s）
- 正文讲解：4.5 字/秒
- 公式/符号密集句：按“有效字数”折算
- 一个 LaTeX 公式块按 8–12 个字等效（取中值 10，或你自行解释采用的换算）
- 每句最短时长：1.6s（避免闪烁）
- 句与句之间可留 0.1–0.2s 缓冲
- 必须输出：每句字数估计/折算字数/时长/总时长

7.3 字幕内容规范（必须）
- 一句只表达一个动作意图：读题、提取条件、设变量、列方程、代入、化简、得结论、检验等
- 避免长句：超过 22–26 字建议拆分两句（各自时间戳）
- 公式建议“口语化 + 局部上屏公式”配合
- 若图片内容有不确定处：字幕中必须显式写 【此处题面不清晰：…】，并给替代版本字幕

8) 解题内容输出粒度要求（图片题通常需要）
- 必须提供两套解题粒度（供我选其一；若我没选，你默认考试版）
  - 考试版（默认）：步骤少但逻辑闭合；每步落到一个等式/结论
  - 讲解版（可选）：补充关键解释、常见坑、条件为什么要这样用
- 每一步对应一个 Step 编号：Step1/Step2/...
- 每个 Step 绑定：
  - equation_tex（可为空）
  - explain_text（一句字幕版本）
  - visual_action（框选/高亮/箭头指向/变色）

9) 全局风格规范（Style Guide，必须）
- 背景：深色纯色或轻微渐变（避免干扰题面）
- 字体策略：中文 Text：思源黑体/微软雅黑（优先可用者）；英文/数字：Arial；公式用 LaTeX
- 字号层级（示例，可给具体数值）：标题 48–56，正文 34–40，注释 28–32，角标/编号 24–28
- 线宽层级：主线 4，辅助线 2–3，高亮框 6
- 高亮色策略：只用 1–2 个强调色；关键条件/关键等式/最终答案颜色一致
- 留白规则：推导区不超过屏幕高度 70%，避免顶到边缘

10) 给“代码生成 AI”的最终总 Prompt（必须，可直接粘贴）
在输出最后，你必须再给一段“总 Prompt”，其结构固定为：
- 强制：ManimGL（3b1b 系）
- 场景类：建议使用 InteractiveScene 或用户自定义 AutoScene
- 必须实现：
  - 原题图导入（可选开关）
  - 题面重排版对象生成
  - Shot List 严格按时间轴执行
  - 字幕系统：第一句 Write，其余 Transform（与时间戳绑定）
  - 关键对象变量命名与分组（便于复用 TransformMatchingTex）
  - 关键参数可配置（字体、字号、颜色、run_time、语速）
- 并附上：
  - 字幕数据结构建议（list[dict] 或 YAML）
  - 时间控制策略（按 t_start/t_end 驱动 wait() 或自定义 time tracker）
  - 若有不确定内容：实现 A/B 两套开关（例如 USE_ORIGINAL_IMAGE=True / False）

解析策略要求（针对图片题，额外补充）
- 任何“可能抄错一个符号就会变题”的地方（±、上下标、积分上下限、向量箭头、集合符号、开闭区间）必须做 confidence 标注
- 若图中有手写：必须提供“手写转标准数学符号”的映射表（例如：像 v 的到底是 ν 还是 v）
- 若图片含多题：必须先拆分题号，再分别输出上述 1–10 项；最后提供一个“总目录镜头”可选
```

### 5.3 AI-1（视频解析）：高精度提示词包 + JSON

```markdown
请对我提供的视频进行内容解析与可复现抽象，输出一份“可直接交给另一个 AI 生成 ManimGL 动画代码”的高精度提示词包，并附最终 JSON 时间轴。解析需覆盖画面元素、分镜结构、动画顺序、时间节奏与文字/公式细节，确保在 ManimGL 中能够被工程化复刻（允许少量视觉近似，但信息结构与时序必须一致）。

你必须输出的内容（必须逐项给出）：
1) 分镜脚本（Shot List，带时间戳）
- Shot 编号
- 时间范围（如 00:12–00:18）
- 画面状态描述（哪些对象在画面上、布局、相对位置）
- 核心变化（新增/消失/移动/变形/颜色变化/缩放/旋转/相机运动）

2) 场景对象清单（Mobject 级别清单）
- 对象名称（建议代码变量名，例如 title, axes, curve, label_1）
- 对象类型（Text/Tex/MathTex/Line/Arrow/Circle/Polygon/NumberPlane/Axes/SVGMobject/ImageMobject 等）
- 样式参数：颜色（hex/RGB/Manim color 常量）、线宽、填充透明度、字体、字号、描边、发光等
- 布局参数：位置（相对屏幕/相对其他对象）、对齐方式（to_edge/next_to/align_to）、缩放比例
- 若存在图像/图标：列出素材文件名与来源（无素材则给占位方案）

3) 动画事件时间轴（ManimGL 动作词 + 参数）
- 发生时间或相对顺序
- 动作类型（ShowCreation, Write, FadeIn, FadeOut, Transform, ReplacementTransform, MoveToTarget, ApplyMethod, GrowArrow, Uncreate 等）
- 动画参数：run_time、rate_func、lag_ratio、path_arc（如有）
- 并行动画关系：哪些动画写在同一个 self.play(...) 中

4) 相机与构图（若视频存在镜头运动）
- Camera frame 初始状态（位置、缩放）
- 每次相机运动的起止时间、目标、缓动
- 是否需要使用 `self.play(self.camera.frame.animate.reorient()）`

5) 文本/旁白/字幕/公式逐字稿（必须精确）
- 按时间戳列出每一段字幕/标题/公式的逐字内容
- 明确使用 Text 还是 Tex/MathTex（需要 LaTeX 的请给出可编译版本）
- 若有高亮/变色/逐词出现：标注对应文字片段与动画方式
- 若有旁白但无字幕：尽可能根据画面推断并标注“不确定内容”，并给替代处理方案（如用简短字幕概括）

6) 全局风格规范（Style Guide）
- 字体选择（中英文字体策略）、字号层级（标题/正文/注释）
- 线条粗细层级、透明度规范

7) 代码生成 AI 的“总 Prompt”（最终交付物）
- 明确：必须用 ManimGL
- 要求：代码注释清晰，关键参数可配置

解析策略要求（保证准确性）：
- 优先保证信息结构、相对布局、出现顺序、关键变换的一致性
- 对于难以辨认的细节：必须显式标注“无法确定/近似处理”，并给 1–2 个可选实现方案

输出最后必须包含“最终 JSON 时间轴”（按工作流 Schema），可直接给 AI-2。
补充对接约束：
- narration 用口语化 TTS 文案，screen_text 用数学化上屏文本；公式优先放 latex。
- visual_action 限定集合；一句一动作，确保可驱动画面。
```

### 5.4 AI-1（PPT 解析）：高精度提示词包 + JSON

```markdown
我将上传一个 .pptx。请你逐页解析该 PPT 的内容细节与呈现逻辑，抽象出可在 ManimGL（3Blue1Brown 体系）中工程化复刻的动画方案。允许少量视觉近似，但信息结构、相对布局、出现顺序、关键变换与节奏必须一致。

你必须输出（逐项给出）：
1) 页级分镜脚本（Slide Shot List，带时间戳或相对时序）
- Slide 编号与标题（若无标题则用“Slide N”）
- 每一步的画面状态（屏幕上有哪些对象、布局、相对位置）
- 每一步的核心变化（新增/消失/移动/变形/颜色变化/缩放/旋转/镜头运动）

2) 场景对象清单（Mobject 级别清单，按“全局复用 + 每页新增”组织）
- 代码变量名建议（如 title, axes, vec_v_ship, label_tmin）
- 类型（Text/Tex/MathTex/Line/Arrow/Polygon/ImageMobject/SVGMobject 等）
- 样式参数（颜色 hex、线宽、填充/透明度、字体、字号、描边/发光）
- 布局参数（相对屏幕位置、对齐方式 to_edge/next_to/align_to、缩放比例）

3) 动画事件时间轴（ManimGL 动作词 + 参数）
- 时刻（绝对秒或相对顺序，如 S3-B2-Event4）
- 动作（Write/FadeIn/FadeOut/Transform/ReplacementTransform/ShowCreation/Uncreate/ApplyMethod 等）
- 参数（run_time、rate_func、lag_ratio、path_arc 等）
- 并行动画关系（哪些写在同一个 self.play(...)）

4) 镜头与构图（若需要 camera frame）
- 初始 frame 位置与缩放
- 每次镜头运动的起止、目标与缓动
- 是否使用 `self.play(self.camera.frame.animate.reorient()）` 的推荐写法

5) 文本/公式逐字稿（必须精确）
- 按页/按 Build 给出每段文字、每条公式的逐字内容
- 若存在逐词出现/高亮变色/下划线框选：标注具体片段与对应动画

6) 全局风格规范（Style Guide）
- 字号层级（标题/正文/注释/角标）
- 颜色与线宽层级、透明度规范
- 对齐栅格与留白规则（保证画面不挤）

7) 给“代码生成 AI”的最终总 Prompt（可直接粘贴）
- 强制：ManimGL
- 要求：代码注释清晰，关键参数可配置

输出最后必须包含“最终 JSON 时间轴”（按工作流 Schema），可直接给 AI-2。
补充对接约束：
- narration 用口语化 TTS 文案，screen_text 用数学化上屏文本；公式优先放 latex。
- visual_action 限定集合；一句一动作，确保可驱动画面。
```

### 5.5 AI-2（ManimGL/AutoScene 代码生成）：严格版提示词

```markdown
你是 ManimGL（manimlib）工程师，请将我提供的 timeline JSON 转为可运行的 AutoScene 代码，竖版 1080x1920，一场景即可。

硬性规范（必须全部满足）：
1) 使用 AutoScene：字幕+TTS 同步；实现 play_t/wait_t/wait_until 驱动时间轴，误差 ≤0.2s；TTS 气口 0.5s；尽量少用 self.wait，仅允许阶段末使用，用动画 run_time 拉齐时间轴。
2) 配音与字幕分离必须支持：speak/speak_with_highlight 中使用 text/subtitle；TTS 文案口语化、字幕更数学化。
3) Tex 禁用 \div，用 ÷；向量用 \overrightarrow{...}；中文 Text 用 STKaiti；数字/字母/公式一律用 Tex；Text 上色用 t2c/text2color；字幕重点用 color_map。
4) 颜色策略：默认文字 WHITE，仅 1 种强调色（建议 RED），强调约 2s 后恢复 WHITE。
5) 相似物体用 Transform/TransformMatchingTex/TransformMatchingShapes；公式首行/无联系用 Write；默认动画 rate_func=smooth, run_time=2（每个 self.play 显式写出）。
6) 坐标轴 include_ticks=False，include_tip=False（如无箭头需求）；x_range/y_range 比例与 width/height 等比，保证单位长度一致。
7) 六块布局（自适应）：Title/Divider/Problem/Viz/Derivation/Subtitle
   - **固定区域**（使用相对定位）：
     - Title: `.to_edge(UP, buff=0.2)` + `fix_in_frame()`
     - Divider: `.next_to(title, DOWN, buff=0.1)`，宽度=`frame_width*0.95` + `fix_in_frame()`
     - Subtitle: 由 AutoScene 管理，`.to_edge(DOWN)` + 自动换行高度
   - **内容区域**（均匀分布）：Problem/Viz/Derivation
     - 使用 `self.layout_content_blocks(problem, viz, derivation, divider=divider)`
     - 算法：divider 底部到 subtitle 顶部的空间内，等间距分布三块中心
   - **简化调用**：`title, divider = self.create_title_divider("【高考真题·概率】")`
   - **左右边距**：`.to_edge(LEFT, buff=0.2)` 或使用 `LAYOUT_EDGE_BUFF`
8) 推导区最后一行必须在字幕上方：使用 `self.get_subtitle_top_y()` 动态获取字幕顶部坐标，确保不重叠。
9) 可视化区至少 1 个 updater 持续运行（ValueTracker+DecimalNumber、游标等），每段重置目标值；静态内容必须加入轻量动态（呼吸高亮/游标/相机微平移等）。
10) 配音段必须有画面动作（Indicate/框选/相机/呼吸高亮），不得长时间静止；开场需“配音+动画+音效”同时出现（如启用音效）。
11) 可视化标签用彩色背景突出；固定标注用 add_fixed_annotation；需要跟随则用 add_fixed_annotation_dynamic。
12) 标题/题目/分割线/推导/字幕/字幕背景默认 fix_in_frame；可视化区不固定。
13) 字幕用 AutoScene：speak/speak_with_highlight 或 subtitle 管线；字幕第一句 Write，后续 Transform。
14) 代码组织：类开头常量区（位置/大小/缩放可调），construct 只做流程调度，setup_scene + phaseN 方法；每阶段前半创建物体，后半统一动画；阶段末清理临时对象，保留共享对象；遮挡关系取决于 self.add 顺序；每阶段开头保留检查机制。
15) 自检输出：打印标题/目标时长/事件信息；可打印每条时间戳便于核对。
16) 需要音效可选 SoundLibrary（若不可用需兼容无音效）；支持 set_animation_sounds_enabled / set_add_sounds_enabled / set_sound_gain。
17) 输出代码要求：完整导入所需模块；中文注释清晰；配音文稿自然流畅；适当使用视觉引导增强效果；代码可直接运行。
18) **遮挡关系取决于 self.add 的顺序**：后 add 的对象 → 在上层 → 遮挡先 add 的对象。
19) **动画播放顺序取决于 self.play 的顺序**：前play的在上层，后play的在下层，被遮挡
        self.play(
  
            ShowCreation(right_arrow),
            ShowCreation(left_arrow),
            run_time=2
        )
20)  高亮line2[1:6]不用line3[0][-9:]
例如：
      line2 = Tex(
            r"\text{点 } (2,4) \text{ 在函数 } f(x) \text{ 的图象上。}",
            font_size=self.PROBLEM_FONT_SIZE
        )
        line2[1:6].set_color(self.HIGHLIGHT_COLOR)  # (2,4) 高亮
  
        line3 = Tex(
            r"\text{当 } x < 0 \text{ 时，} f(x) = x^2 + bx",
            font_size=self.PROBLEM_FONT_SIZE
        )
        line3[0][-9:].set_color(self.HIGHLIGHT_COLOR)  # 公式高亮
输出：仅代码，不要解释。请在代码里内联 JSON（或假设变量 timeline），并严格按时间轴执行。
JSON：<粘贴 timeline JSON>
```

### 5.6 提示词补丁（可直接拼进总 Prompt）

#### 5.6.1 排版与动态补丁

```markdown
排版强约束：六块顺序 Title/Divider/Problem/Viz/Derivation/Subtitle；左右边距≤画幅 5%(≤0.2)，安全宽 W=frame_w-2m，目标占宽 92~95%，先换行控 max_w=0.95W，再合并/放大到 target_fill≈0.92W，避免细长条；统一 buff 垂直排列，gap 不够时优先缩 Subtitle→Derivation→Problem，Viz 保底高度≥0.28*frame_h，最终 group 左对齐。

可视化动态：每段至少 1 个 updater（ValueTracker+DecimalNumber、游标沿路径、呼吸高亮等），按时间段重置目标值，配音段不得静止。
```

#### 5.6.2 配音与字幕分离补丁

```markdown
配音与字幕分离：speak()/speak_with_highlight() 中用 text 作为 TTS 文稿、subtitle 作为屏幕显示。
- 负号：text="f 负 2 等于 负 4"，subtitle="f(-2) = -4"
- 等号：text="a 等于 5"，subtitle="a = 5"
- 坐标：text="坐标 2 4"，subtitle="(2, 4)"
- 小于：text="x 小于 0"，subtitle="x < 0"
- 平方：text="x 平方"，subtitle="x2"
```

#### 5.6.3 “同质化特征”提取提示

```markdown
从给定代码/视频中提取可复刻特征，生成简明 md：
- 字体策略（如 Text 用 STKaiti）
- 动画衔接（相似物体 Transform，避免 FadeOut+FadeIn）
- 代码组织（常量区 + construct 调度 + phaseN 方法 + 时间驱动三件套）
- 颜色/高亮策略（默认白，强调短暂变红）
- 时间对齐策略（按时间轴播放/等待）
要求输出：紧凑 bullet，供其他 AI 复用风格。
```

## 6. 代码骨架与算法模板（可直接复用）

### 6.1 时间轴驱动三件套

```python
# 时间轴驱动器（必须实现）
self.t = 0  # 全局时间指针

def play_t(self, *anims, rt=1):
    self.play(*anims, run_time=rt, rate_func=smooth)
    self.t += rt

def wait_t(self, dt):
    self.wait(dt)
    self.t += dt

def wait_until(self, target):
    if target > self.t:
        self.wait_t(target - self.t)
```

### 6.2 AutoScene 场景骨架（推荐）

```python
import os
import sys
import numpy as np

# 添加 AutoScene 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
auto_scene_dir = r"E:\auto_manim\new_class"
if auto_scene_dir not in sys.path:
    sys.path.insert(0, auto_scene_dir)

from auto_scene import AutoScene
from manimlib import *

class 场景名(AutoScene):
    # ========== 常量区（可调试入口） ==========
    TITLE_Y = 5.5
    PROBLEM_Y = 3.5
    VIZ_Y = 0.8
    SOLUTION_Y = -2.2
    SCREEN_WIDTH = 27/4
    TITLE_FONT_SIZE = 24
    PROBLEM_FONT_SIZE = 24
    SOLUTION_FONT_SIZE = 24

    def construct(self):
        self.setup_scene()
        self.phase1_title()
        self.phase2_problem()
        self.phase3_viz_and_derivation()
        self.phase4_summary()

    def setup_scene(self):
        self.enable_debug(True)
        self.set_subtitle_style(font_size=22, edge_buff=0.3)
        self.shared_objects = {}

    def phase1_title(self):
        # 先创建对象并摆放，再统一动画
        pass

    def phase2_problem(self):
        pass

    def phase3_viz_and_derivation(self):
        pass

    def phase4_summary(self):
        pass
```

### 6.3 六块布局使用示例（推荐）

```python
# 使用 AutoScene 内置的六块布局方法（自适应定位）
class LayoutDemo(AutoScene):
    def construct(self):
        self.setup_scene()
        self.phase1_title()
        self.phase2_content()
    
    def setup_scene(self):
        self.enable_debug(True)
        self.set_subtitle_style(font_size=22, edge_buff=0.3)
        self.shared_objects = {}
    
    def phase1_title(self):
        # 使用 create_title_divider 创建标题和分割线（自动定位+fix_in_frame）
        title, divider = self.create_title_divider("【高考真题·概率】")
        
        self.play(FadeIn(title), rate_func=smooth, run_time=0.5)
        self.play(FadeIn(divider, shift=LEFT * 10), rate_func=smooth, run_time=0.8)
        
        self.shared_objects["title"] = title
        self.shared_objects["divider"] = divider
    
    def phase2_content(self):
        # 1. 创建三个内容块（先不指定位置）
        problem = Tex(r"题目：已知集合 $P=\{-1,0,1,2,3,4\}$...", font_size=22)
        
        viz = VGroup(
            Axes(x_range=[-2, 5], y_range=[-3, 4], width=5, height=4),
            # ... 可视化内容
        )
        
        derivation = Tex(r"解：样本空间 $n=36$，满足条件 $m=3$", font_size=22)
        
        # 2. 使用 layout_content_blocks 自动布局（等间距分布）
        divider = self.shared_objects["divider"]
        layout_info = self.layout_content_blocks(
            problem, viz, derivation,
            divider=divider  # 传入分割线获取上边界
        )
        # layout_info = {"top_y", "bottom_y", "gap", "centers": [...]}
        
        # 3. 显示内容
        self.add(problem, viz, derivation)
        self.play(Write(problem), run_time=1)
        self.play(ShowCreation(viz), run_time=1)
        self.play(Write(derivation), run_time=1)
```

**布局方法说明**：
- `create_title_divider(title_text)`: 创建标题+辉光分割线，自动 `.to_edge(UP)` + `fix_in_frame()`
- `layout_content_blocks(problem, viz, derivation, divider=)`: 均匀分布内容块，自动计算间距
- `get_subtitle_top_y()`: 动态获取字幕顶部 Y 坐标（适应换行）
- `get_content_center_y(index, divider=)`: 获取指定块的中心 Y 坐标
```


### 6.4 可视化动态模板（Updater 必须）

```python
# 可视化区“动态展示”模板
# 必须有 ValueTracker t，并在段落内 t.animate.set_value(1)
import numpy as np

def add_dynamic_indicator(self, viz_group, t_start, t_end):
    t = ValueTracker(0)

    # 示例：数值显示
    decimal = DecimalNumber(0, num_decimal_places=2)
    decimal.add_updater(lambda d: d.set_value(10 * t.get_value()))

    # 示例：游标移动
    path = Line(LEFT, RIGHT)
    cursor = Dot(color=YELLOW)
    cursor.add_updater(lambda c: c.move_to(path.point_from_proportion(t.get_value())))

    # 示例：呼吸高亮
    rect = SurroundingRectangle(viz_group, buff=0.1)
    rect.add_updater(lambda r: r.set_stroke(width=2 + 2*np.sin(2*np.pi*t.get_value())))

    self.add(decimal, cursor, rect)
    self.play(t.animate.set_value(1), run_time=t_end - t_start, rate_func=linear)
```

### 6.5 自检输出模板

```python
def construct(self):
    # 渲染前自检
    print("="*50)
    print(f"视频标题: {self.meta['title']}")
    print(f"目标时长: {self.timeline[-1]['end']}s")
    print("="*50)

    for e in self.timeline:
        duration = e['end'] - e['start']
        if duration < 0:
            raise ValueError(f"负时长！事件: {e['scene_id']}")
        print(f"[{e['start']:.1f}-{e['end']:.1f}] {e['visual_action']}: {e['narration'][:20]}...")
```

## 7. 专项任务：音稿时间戳同步

### 7.1 任务目标

1) 根据文稿时间戳，Indicate 对应屏幕已有的文本对象，所有显示在屏幕上的文本对象都需要被强调至少一遍
2) 简略屏幕上已有的文本对象内容，以便字号更大
3) 文字颜色默认 WHITE，只在重点短暂变色
4) 时间轴严格对齐（核心）
5) 额外输出一份“保留原版可视化逻辑”的修改版代码文件
6) 动画总时间控制为 126s
7) 加入 `print()` 每一个时间戳的逻辑
8) 尽量少使用 `self.wait()`，只允许在阶段结束时使用

### 7.2 具体实现要点

- 颜色策略：默认 WHITE，仅 1 种强调色（建议 RED），强调持续 2s 后恢复 WHITE
- 时间轴对齐：使用时间轴驱动器三件套（见 6.1），误差 ≤ 0.2s
- 文本精简：缩短字幕/文本内容以提升字号与可读性
- 强调覆盖：所有屏幕文字至少被 Indicate 一次
- 提取音稿及其起止时间戳，列出更细粒度时间轴清单

## 8. 待办事项

- [ ] 常用音效库整理
- [ ] 配音网站推荐列表
- [ ] 视频剪辑模板
- [ ] ManimGL 代码模板库
- [ ] 常用音效库整理（附 `SoundLibrary` 类）
- [ ] JSON Schema 校验工具
- [ ] 时间轴可视化预览工具

---

如需扩展：`auto_wrap.py` 可直接在生成代码中用于 Text/Tex 自动换行（贪心控宽、支持中英文混排）。
