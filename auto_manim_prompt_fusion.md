# auto_manim 提示词融合手册

面向 ManimGL + AutoScene 的统一提示词与规范，合并项目内所有提示词与硬性约束，直接粘贴即可用。

---

## 目录

- [1. AutoScene/ManimGL 能力速查](#1-autoscenемanimgl-能力速查)
  - [1.1 配音与字幕](#11-配音与字幕)
  - [1.2 视觉引导与标注](#12-视觉引导与标注)
  - [1.3 相机与固定元素](#13-相机与固定元素)
  - [1.4 辉光与脉动](#14-辉光与脉动)
  - [1.5 调试与时间](#15-调试与时间)
  - [1.6 布局辅助](#16-布局辅助)
  - [1.7 坐标轴与箭头（New）](#17-坐标轴与箭头new)
  - [1.8 呼吸效果（New）](#18-呼吸效果new)
  - [1.9 默认常量](#19-默认常量可通过-set_subtitle_style-覆盖)
- [2. 工作流总览](#2-工作流总览)
- [3. 阶段独立性原则（Phase Independence）](#3-阶段独立性原则phase-independence)
  - [3.1 问题背景](#31-问题背景)
  - [3.2 解决方案：安全共享对象访问](#32-解决方案安全共享对象访问)
  - [3.3 代码规范](#33-代码规范)
  - [3.4 测试方式](#34-测试方式)
- [4. JSON Schema 与 visual_action 映射](#4-json-schema-与-visual_action-映射)
  - [4.1 最小 Schema](#41-最小-schema)
  - [4.2 推荐 Schema（完整版）](#42-推荐-schema完整版)
  - [4.3 visual_action → 动画映射](#43-visual_action--动画映射)
- [5. 提示词库（可直接复制）](#5-提示词库可直接复制)
  - [5.1 AI-1（题目图片输入）](#51-ai-1题目图片输入完整版提示词)
  - [5.2 AI-1（视频解析）](#52-ai-1视频解析高精度提示词包--json)
  - [5.3 AI-1（PPT 解析）](#53-ai-1ppt-解析高精度提示词包--json)
  - [5.4 AI-2（ManimGL/AutoScene 代码生成）](#54-ai-2manimglautoscene-代码生成严格版提示词)
- [6. 代码骨架与算法模板](#6-代码骨架与算法模板可直接复用)
  - [6.1 时间轴驱动三件套](#61-时间轴驱动三件套)
  - [6.2 AutoScene 场景骨架](#62-autoscene-场景骨架推荐)
  - [6.3 六块布局使用示例](#63-六块布局使用示例推荐)
  - [6.4 可视化动态模板](#64-可视化动态模板updater-必须)


---

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

### 1.5 GPU 辉光与彗尾 (GPU Glow)

- `create_glow_curve(function, t_range, ...)`：基于着色器的 GPU 辉光曲线
- `create_glow_function_graph(function, x_range, ...)`：GPU 辉光函数图
- `create_glow_wrapper(mobject, ...)`：为任意对象添加 GPU 辉光包裹
- `create_glow_point_cloud(points, colors, ...)`：GPU 辉光点云
- `TracingTailPMobject(...)`：辉光彗尾效果 (需要 shaderscene)
- `create_glow_surrounding_rect(...)`：软件模拟辉光方框 (兼容性好)

### 1.6 调试与时间

- `enable_debug` / `enable_time_hud`
- `mark` / `get_markers` / `get_current_time`

### 1.6 布局辅助

- `ensure_above_subtitle(mobject, viz_bottom_y=None, margin=0.3, overlap_buff=0.2)`
- `create_title_divider(title_text, ...)`：创建标题+自适应辉光分割线
- `layout_content_blocks(problem, viz, derivation, ...)`：自动均匀分布内容块
- `get_subtitle_top_y()`：动态获取字幕顶部坐标
- `get_content_center_y(block_index, ...)`：获取块中心 y 坐标 (0=Prob, 1=Viz, 2=Deriv)

### 1.7 坐标轴与箭头（New）

- `StealthTip(angle, width, length, back_indent)`：仿 TikZ stealth 尖锐箭头
- `add_stealth_tip_to_line(line, ...)`：为线添加 stealth 箭头
- `create_stealth_axes(...)`：创建带指定范围和 stealth 箭头的坐标轴
- `create_stealth_axes_with_labels(...)`：创建带标签的 stealth 坐标轴

### 1.8 呼吸效果（New）

- `create_breathing_glow_dot(center, mode, ...)`：创建呼吸辉光点（basic/rainbow/heartbeat/pulse/wave）
- `BreathingModeManager` / `next_breathing_mode()`：呼吸模式管理

### 1.9 默认常量（可通过 set_subtitle_style 覆盖）

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

### 5.1 AI-1（题目图片输入）：完整版提示词

```markdown
你是短视频脚本与时间轴编排器。请基于我给出的题目图片（可含文字补充），生成可直接驱动 ManimGL/AutoScene 的「时间轴 JSON + 题面解析材料」。目标：不抄错、不漏条件，时间轴可执行。

【输入信息（请填写）】
1) 图片类型：截图/照片/扫描件/拼接图
2) 题目来源：【高考真题·函数综合】/【竞赛·几何】等
3) 期望解法风格：考试版/讲解版/竞赛版
4) 目标时长：60s / 3min / 8min
5) 讲解深度：只讲关键步骤 / 讲完整推导

【素材】
- 题目图片：<粘贴图片>
- 补充文字：<可选>
- 附加上下文：<粘贴来源/时长/深度等>

【总规则（必须遵守）】
1) 字速：intro 5 字/s，middle 4.5 字/s，outro 5 字/s；时间精度 0.1s，严格递增不重叠。
2) 停顿：句末 0.2–0.4s；转场 0.6–1.0s（单独事件，visual_action="转场"）。
3) 每句字段：scene_id，section(intro/middle/outro)，start，end，narration，screen_text，latex，visual_action（限定：标题/定义/示意图/推导/例题/强调/小结/转场）。
4) 总时长控制在 [60,90]s（如未指定以此为准）。
5) 图片题特有：先抽取题面关键信息并重排成“上屏版”；公式用可编译 LaTeX；不确定处用【?】标注，避免臆测。
6) 讲解与上屏分离：narration 用口语化 TTS 文案，screen_text 用更“数学化”的上屏文本；公式优先放在 latex 字段。
示例（口语 vs 上屏）：
- narration: "x 小于 0"
- screen_text: "x < 0"
- latex: "x < 0"
7) 一句一动作：每句只表达一个动作意图，visual_action 必须可驱动对应画面变化。
示例（一句一动作拆分）：
- 错误：首先设 x=a，代入方程，化简得到 x^2=4
- 正确1：首先，设 x=a（visual_action=定义）
- 正确2：代入原方程（visual_action=强调）
- 正确3：化简得到 x^2=4（visual_action=推导）
8) 题面自动换行：每行≤16等效字符（中文1字=1单位，英文2字符=1单位，行内公式整体按10单位计且不可拆），优先在标点/虚词/公式前后换行，禁止在公式内部换行；输出 problem_lines[] 数组。

【解析策略要求（图片题必做）】
- 任何“可能抄错一个符号就会变题”的地方（±、上下标、积分上下限、向量箭头、集合符号、开闭区间）必须做 confidence 标注。
- 若图中有手写：必须提供“手写转标准数学符号”的映射表（例如：像 v 的到底是 ν 还是 v）。
- 若图片含多题：必须先拆分题号，再分别输出下述 A–K；最后提供一个“总目录镜头”可选。

【输出格式（必须按顺序输出；除以下内容外不要额外解释）】

A) 题面信息抽取与可靠性标注（必须）
- 结构化 OCR + 版面理解
- 题目逐字稿（原题面）
- 分块输出：标题/题干/小问(1)(2)(3)/已知条件/图形标注/表格/注释
- 每块给出：content（公式用可编译 LaTeX）、type（Text/MathTex/纯符号/图形标注）、confidence（高/中/低；低则必须给 A/B 替代方案）、uncertain_spans（不确定片段用【?】）
- 图形/示意图解析：几何对象/坐标轴/曲线/阴影/箭头/表格列标题等；不确定要写原因（如遮挡/像素/倾斜/光照）+近似方案 A/B
- 版面布局摘要：block_name: bbox=(x0,y0,x1,y1)，x,y ∈ [0,1]，以屏幕左下为 (0,0)
- 目标：保证题目内容不会抄错/漏条件/漏符号；低置信度必须给两套可执行方案

B) 可复刻的“题目重排版”版本（必须）
- 标题（可选）、题干按语义断行、公式给 LaTeX、小问编号统一
- 若有图：给出复刻版或“保留原图 + 框选 + 标注”的替代策略
- 必须同时提供：
  - DisplayVersion：最终上屏文本/公式（可直接变成 Text/Tex/MathTex）
  - SourceMapping：每一行对应原图哪个信息块（便于校对）

C) 分镜脚本（Shot List，必须）
- 至少 1s 精度；Shot 编号、时间范围（例如 00:00–00:06）、画面状态描述、核心变化、讲解意图
- 推荐镜头：开场 → 题面聚焦 → 题面净化 → 解题主线 → 结果汇总

D) 场景对象清单（Mobject 级别，必须）
- 变量名建议、类型、样式、布局、复用关系
- 全局对象/题面对象/解题对象分组

E) 动画事件时间轴（ManimGL 动作词 + 参数，必须）
- 时间点（绝对秒或相对序号）
- 动作类型：ShowCreation / FadeIn / FadeOut / Write / Transform / ReplacementTransform / Indicate / Wiggle / Flash / ApplyMethod / MoveToTarget / Uncreate 等
- 参数：run_time、rate_func、lag_ratio、path_arc（如有）
- 并行动画：同一个 self.play(...) 里有哪些动画同时发生
- 与字幕同步：对应 subtitle_id
- 题面重排版必须指定 TransformMatchingTex / ReplacementTransform / FadeTransformPieces 或 Fade
- 推导链说明：新公式是 Write 还是由旧公式 Transform 而来

F) 相机与构图（若需要，必须）
- 初始 camera frame：位置/缩放
- 每次镜头运动：起止时间、目标区域、缓动函数
- 推荐写法：self.play(self.camera.frame.animate.scale(...).move_to(...), ...)
- 若不需要相机运动，明确写“无相机运动”

G) 字幕文稿与旁白稿要求（必须）
G1) 字幕清单格式（表格或 YAML/JSON 均可）
- id, t_start, t_end, text, mode(title/subtitle/narration/equation_hint), on_screen, action_hint, anchor, pace_note
- 第一条：Write；后续：Transform 上一句 → 下一句
G2) 字幕时长生成规则（必须写明并执行）
- 开场字幕：5 字/秒（或等效英文 12–15 chars/s）；正文：4.5 字/秒
- 公式块按 8–12 字等效（默认 10）
- 每句最短时长 1.6s；句间缓冲 0.1–0.2s
- 必须输出：每句字数估计/折算字数/时长/总时长
G3) 字幕内容规范
- >22–26 字需拆句
- 公式建议“口语化 + 局部上屏公式”配合
- 若图片不清晰：字幕中必须显式写【此处题面不清晰：...】并给替代版本

H) 解题内容输出粒度要求（必须提供两套）
- 考试版（默认）与讲解版（可选）
- 每一步 Step1/Step2/...，绑定：equation_tex（可为空）/explain_text（一句字幕版本）/visual_action

I) 全局风格规范（Style Guide，必须）
- 背景：深色纯色或轻微渐变（避免干扰题面）
- 字体策略：中文 Text 用思源黑体/微软雅黑（优先可用者），英文/数字用 Arial，公式用 LaTeX
- 字号层级：标题 48–56，正文 34–40，注释 28–32，角标 24–28（可给具体数值）
- 线宽层级：主线 4，辅助线 2–3，高亮框 6
- 高亮色策略：只用 1–2 个强调色；关键条件/关键等式/最终答案颜色一致
- 留白规则：推导区不超过屏幕高度 70%，避免顶到边缘

J) 给“代码生成 AI”的最终总 Prompt（必须，可直接粘贴）
- 强制：ManimGL（3b1b 系）
- 场景类：InteractiveScene 或 AutoScene
- 必须实现：原题图导入（可选开关）、题面重排版对象生成、Shot List 严格按时间轴执行
- 字幕系统：第一句 Write，其余 Transform（与时间戳绑定）
- 关键对象变量命名与分组（便于复用 TransformMatchingTex）
- 关键参数可配置（字体/字号/颜色/run_time/语速）
- 并附上：字幕数据结构建议（list[dict] 或 YAML）、时间控制策略（按 t_start/t_end 驱动 wait() 或 time tracker）
- 若有不确定内容：实现 A/B 两套开关（例如 USE_ORIGINAL_IMAGE=True / False）

K) 最终 timeline JSON（必须）
- 仅此处输出 JSON；JSON 可放在标注为 json 的代码块中，块内不得夹杂非 JSON 内容
- 必须满足字段：scene_id/section/start/end/narration/screen_text/latex/visual_action
- visual_action 只能来自限定集合
- 必须包含 problem_lines[]（题面自动换行后的数组）
- total_duration 与目标时长一致
```

**图片工作流快速步骤**

1) 发题目图片 + 上下文 → 用 5.1 提示词生成 JSON
2) 检查 JSON → 人工校对时间戳/公式/旁白
3) 发给 AI-2 → 生成 AutoScene 代码（见 5.5）
4) 运行调试 → `self.enable_debug(True)` 逐阶段检查
5) 渲染输出 → `manimgl script.py SceneName -w --resolution 1080x1920`

### 5.2 AI-1（视频解析）：高精度提示词包 + JSON

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

### 5.3 AI-1（PPT 解析）：高精度提示词包 + JSON

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

### 5.4 AI-2（ManimGL/AutoScene 代码生成）：严格版提示词

```markdown
你是 ManimGL（manimlib）工程师，请将我提供的 timeline JSON 转为可运行的 AutoScene 代码，竖版 1080x1920，一场景即可。

# ⚠️ 【最高优先级】六块布局规范（必须严格遵守）

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔒 Title (标题区)                              ┃ fix_in_frame
┃  ━━━ Divider (分割线) ━━━━━━━━━━━━━━━━━━━━━━━━━ ┃ fix_in_frame
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  📋 Problem (题目区)                            ┃ 不固定
┃     └─ 题目文字、条件、小问                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  📊 Viz (可视化区) ← 必须有 updater + 图形！    ┃ 不固定
┃     └─ ValueTracker + DecimalNumber 动态数值    ┃
┃     └─ 抽象图形：用简化图标描述题目元素         ┃
┃        鸡🐔=黄圆+三角嘴+两个线条脚 兔🐰=灰椭圆+长耳+四个线条脚         ┃
┃        点=Dot 区域=Rectangle 向量=Arrow         ┃
┃     └─ 动态动画：图形数量/位置随数值变化        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  📝 Derivation (推导区) ← 公式居中！            ┃ 不固定
┃     └─ 推导公式（居中对齐，不要左对齐）         ┃
┃     └─ TransformMatchingShapes 变换             ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  🔒 Subtitle (字幕区)                           ┃ fix_in_frame (AutoScene管理)
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**布局硬性要求**：
- 六块顺序：Title/Divider/Problem/Viz/Derivation/Subtitle
- Problem/Viz/Derivation 三区必须存在且**均匀分布**
- **⚠️ Viz 可视化区域必须始终保持存在，不能消失！** 推导区在 Viz 下方进行
- Viz 区域必须包含：
  - 至少一个 updater（ValueTracker/DecimalNumber/游标）
  - **抽象图形表示**：用简化几何图形描述题目元素
    - 鸡=黄色圆+三角嘴+**2条腿（Line）**
    - 兔=灰色椭圆+长耳+**4条腿（Line）**
    - 腿数必须可视化（用 Line 绘制，颜色 ORANGE）
  - 图形数量/位置随数值变化
- Derivation 区域公式必须**居中对齐**（`.set_x(0)`），禁止左对齐
- 固定元素：Title/Divider/Subtitle/网格/红绿灯 使用 fix_in_frame；题目/推导/可视化默认不固定
- **边距规范**：标题区 `0.4`、分割线 `0.2`、内容区 `0.15`、左右 `0.2`
- **文本宽度**：W=frame_w-2m（m=左右边距），AutoWrap 先控 max_w≈0.95W，目标填充≈0.92W（最低 0.85W）
- **垂直压缩优先级**：空间不足时缩 Subtitle→Derivation→Problem，Viz 保底高度≥0.28*frame_h
- **最终对齐**：内容组整体左对齐

## 📐 均匀分布 API（⚠️ 必须使用）

```python
# 1. 先创建所有内容块（不设置位置）
problem_group = VGroup(problem, method_title).arrange(DOWN, buff=0.15)
viz_group = create_viz_content()  # 可视化区域
derivation_group = create_derivation_content()  # 推导区域

# 2. 使用 layout_content_blocks 均匀分布三区（自动放大 viz 到 88% 宽度）
layout_info = self.layout_content_blocks(
    problem=problem_group,
    viz=viz_group,
    derivation=derivation_group,
    divider=divider,
    align_left=False,           # 居中对齐
    scale_viz=True,             # 自动放大 viz（默认 True）
    viz_width_ratio=0.88,       # viz 目标宽度比例（默认 88%）
)
# 返回值: {"top_y", "bottom_y", "gap", "centers", "mode"}

# 3. 调整 problem 左对齐（如需要）
problem_group.to_edge(LEFT, buff=0.2)
```

## ⚠️ 遮挡处理规范（重要）

**防御性手段**：当元素过多、字号大或背景网格干扰公式阅读时，**必须**为文字/公式添加黑色背景块以确保清晰度。

### 1. 为文字/公式添加黑色背景（BackgroundRectangle）
```python
from manimlib import BackgroundRectangle

# 推荐写法：创建带背景的文字组
text = Tex(r"重要公式", font_size=42)
bg = BackgroundRectangle(text, fill_opacity=0.9, buff=0.15)
text_with_bg = VGroup(bg, text)  # 背景在下，文字在上
```

### 2. 动态降低背景透明度 (Opacity Dimming)
当推导公式可能与背景的可视化区域产生重叠时，动态降低背景图标/图像的透明度（如从 1.0 降到 0.3），以确保前景公式极度清晰。

```python
# 使用 ValueTracker 控制背景透明度
opacity_tracker = ValueTracker(1.0)
viz_group.add_updater(lambda m: m.set_opacity(opacity_tracker.get_value()))

# 当开始推导重要公式时，淡化背景
self.play(opacity_tracker.animate.set_value(0.3), run_time=1)
# ... 进行公式演示 ...
# 后期如需强调可视化，再恢复
self.play(opacity_tracker.animate.set_value(1.0), run_time=1)
```

### 3. 字号规范（硬性要求）
- **公式最小默认字号：42**（确保在手机刷视频时清晰可见）
- 关键结论/答案字号：44-48
- 标题区域字号：24-28
- 题目描述字号：22-26

## 📊 Viz 可视化区域详细规范

### 基础可视化（所有题目必备）

```python
# ValueTracker + DecimalNumber 动态数值
tracker = ValueTracker(初始值)
count = DecimalNumber(初始值, num_decimal_places=0, font_size=18)
count.add_updater(lambda m: m.set_value(tracker.get_value()))

# 动态演示
self.play(tracker.animate.set_value(目标值), run_time=3)
```

### 函数题目专用 API（⚠️ 函数题必须使用）

```python
from new_class.auto_scene import (
    create_stealth_axes,        # 创建 TikZ 风格坐标轴
    create_glow_surrounding_rect,  # 辉光方框
    is_gpu_glow_available,      # 检测 GPU 辉光支持
)

# 1. 创建坐标轴（StealthTip 箭头风格）
stealth_axes = create_stealth_axes(
    x_range=[-6, 6, 1],
    y_range=[-6, 6, 1],
    axis_config={"stroke_width": 1.5, "color": WHITE},
    tip_config={"tip_length": 0.25, "tip_width": 0.2, "back_indent": 0.3},
    width=4.0,
    height=4.0,
).move_to(UP * VIZ_Y)

# 获取底层 Axes 对象
axes = stealth_axes.axes

# 添加轴标签
x_label = Tex("x", font_size=16).next_to(stealth_axes.x_tip, RIGHT, buff=0.1)
y_label = Tex("y", font_size=16).next_to(stealth_axes.y_tip, UP, buff=0.1)

# 2. 动态曲线（参数随 ValueTracker 变化）
b_tracker = ValueTracker(0)

def get_dynamic_curve():
    b = b_tracker.get_value()
    return axes.get_graph(
        lambda x: x**2 + b*x,
        x_range=[-5, -0.1],
        color=BLUE,
        stroke_width=2
    )

dynamic_curve = always_redraw(get_dynamic_curve)
self.add(dynamic_curve)

# 动画：参数从 0 变化到 4
self.play(b_tracker.animate.set_value(4), run_time=3)

# 3. GPU 辉光曲线（高级效果）
if is_gpu_glow_available():
    glow_curve = stealth_axes.get_glow_graph(
        function=lambda x: x**2 + 4*x,
        x_range=[-5.5, -0.1],
        color=BLUE,
        n_samples=500,
    )
    self.add(glow_curve)

# 4. 关键点辉光
if is_gpu_glow_available():
    glow_dots = stealth_axes.get_glow_dots(
        coords=[(2, 4), (-2, -4)],
        colors=[YELLOW, YELLOW],
        glow_width=0.3,
    )
    self.add(glow_dots)

# 5. 关键点标签 + 辉光背景
point_label = Tex("(2,4)", font_size=14)
point_label.move_to(axes.c2p(2, 4) + UR * 0.2)
point_bg = create_glow_surrounding_rect(
    point_label, color=RED, buff=0.03,
    stroke_width=1, fill_opacity=0.6,
)
self.play(FadeIn(point_bg), Write(point_label))
```

### 题型对应可视化

| 题型 | 可视化内容 | 必用 API |
|-----|-----------|---------|
| 鸡兔同笼 | 鸡兔图标+腿+数量 | VGroup, Circle, Line, DecimalNumber |
| 函数 | 坐标轴+动态曲线+关键点 | create_stealth_axes, get_graph, always_redraw |
| 概率 | 样本空间网格+标记点 | NumberPlane, Rectangle, Dot |
| 几何 | 几何图形+标注 | Polygon, Line, Arrow, Tex |
| 数列 | 序列图+递推箭头 | VGroup, Arrow, DecimalNumber |

# 硬性规范（必须全部满足）

1) 使用 AutoScene：字幕+TTS 同步；实现 play_t/wait_t/wait_until 驱动时间轴，误差 ≤0.2s；TTS 气口 0.5s；尽量少用 self.wait，仅允许阶段末使用，用动画 run_time 拉齐时间轴。

2) **数学符号规范（⚠️ 重要）**：
   - ❌ 禁止使用 `\div`（ManimGL 渲染不正确）
   - ✅ 必须直接使用 `÷` 符号（Unicode: U+00F7）
   - 示例：`Tex(r"12 ÷ 2 = 6")` 而非 `Tex(r"12 \div 2 = 6")`
   - 向量用 `\overrightarrow{...}`
   - 中文 Text 用 STKaiti
   - 包含复杂公式一律用 Tex
   - Tex 上色要另起一行，切片数组单独上色

3) 颜色策略：默认文字 WHITE，仅 1 种强调色（建议 RED），强调频率每阶段 1–2 次，约 2s 后恢复 WHITE。

4) 动画选择：相似物体用 Transform/TransformMatchingTex/TransformMatchingShapes；公式首行/无联系用 Write；默认 rate_func=smooth, run_time=2（每个 self.play 显式写出）。

5) 坐标轴 include_ticks=False，include_tip=False（如无箭头需求）；x_range/y_range 比例与 width/height 等比，保证单位长度一致。

6) 推导区最后一行必须在字幕上方：使用 `self.get_subtitle_top_y()` 动态获取字幕顶部坐标，确保不重叠。

7) 可视化区至少 1 个 updater 持续运行（ValueTracker+DecimalNumber、游标等），每段重置目标值；静态内容必须加入轻量动态（呼吸高亮/游标/相机微平移等）。

8) 配音段必须有画面动作（Indicate/框选/相机/呼吸高亮），不得长时间静止；开场需“配音+动画+音效”同时出现（如启用音效）。

9) 可视化标签用彩色背景突出；固定标注用 add_fixed_annotation；需要跟随则用 add_fixed_annotation_dynamic。

10) 代码组织：类开头常量区（位置/大小/缩放可调），construct 只做流程调度，setup_scene + phaseN 方法；每阶段前半创建物体，后半统一动画；阶段末清理临时对象，保留共享对象；每阶段开头保留检查机制。

11) 自检输出：打印标题/目标时长/事件信息；可打印每条时间戳便于核对。

12) 需要音效可选 SoundLibrary（若不可用需兼容无音效）；支持 set_animation_sounds_enabled / set_add_sounds_enabled / set_sound_gain。

13) 输出代码要求：完整导入所需模块；中文注释清晰；配音文稿自然流畅；适当使用视觉引导增强效果；代码可直接运行。

14) 层级规则：遮挡关系由 self.add 顺序决定（后 add 在上层）；self.play 顺序仅影响时间，不改变层级。

15) Tex 切片高亮示例（优先使用线性切片，避免不稳定嵌套索引）：
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
JSON：<粘贴 timeline JSON>

【配音与字幕分离规范】
- speak()/speak_with_highlight() 或 subtitle 管线；text 作为口语化 TTS 文稿、subtitle 作为数学化上屏
- 字幕动画：第一句 Write，后续 Transform 上一句 → 下一句
- 常见映射：
  - 坐标：text="坐标 2 4"，subtitle="(2, 4)"
  - 小于：text="x 小于 0"，subtitle="x < 0"
  - 平方：text="x 平方"，subtitle="x²"
  - 函数：text="f x 等于"，subtitle="f(x) ="
示例：
```python
self.speak(
    text="f 2 等于 4",
    subtitle="f(2) = 4",
)
```

【动画衔接与引导】
- 重点覆盖：所有屏幕文字至少被 Indicate 或高亮一次。
- 引导方框：使用 `focus_guide` 或 `focus_guide_with_camera` 进行视线引导；方框颜色轮询。
- 呼吸点：关键数据或游标建议使用 `create_breathing_glow_dot`。
- 标注：使用 `add_curved_annotation` 且开启 `use_glow=True`。

【Tex 自动换行与公式完整性】
换行阈值：每行≤16个等效字符（中文1字=1单位，英文2字符=1单位，行内公式整体按10单位计且不可拆）

换行优先级：
1. 数学符号前后（如 ∈、∪、= 前后）
2. 标点后（，。；）
3. 虚词后（"的"、"是"、"在"、"与"、"和"）
4. 行内公式前后（公式块本身不拆）

禁止：
- 在 $...$ 内部换行
- 在 \text{...} 内部中间换行
- 产生只有1-2字的碎片行
- 单行过长 Tex（超过屏幕 90%）
- 使用 stretch_to_fit_width 强制压缩（会变形）

代码实现示例：
```python
# ✅ 正确：多行分别创建（公式不拆）
problem_lines = [
    r"\text{17. (10分) 已知函数 } f(x) \text{ 是定义在}",
    r"(-\infty,0) \cup (0,+\infty) \text{ 上的奇函数，}",
    r"\text{点 } (2,4) \text{ 在函数 } f(x) \text{ 的图象上。}",
    r"\text{当 } x < 0 \text{ 时，} f(x) = x^2 + bx",
]

problem_group = VGroup(*[
    Tex(line, font_size=24) for line in problem_lines
]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

# 高亮第3行的 (2,4)
problem_group[2][1:6].set_color(YELLOW)
```
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
        self.set_animation_sounds_enabled(True)  # 启用动画音效
        self.shared_objects = {}

    def phase1_title(self):
        # ✅ 使用内置方法创建标题和分割线
        title, divider = self.create_title_divider("【高考真题·函数】")
        self.play(FadeIn(title), ShowCreation(divider))
        self.set_shared("title", title)
        self.set_shared("divider", divider)

    def phase2_problem(self):
        # ✅ 使用 get_shared 获取前序对象
        divider = self.get_shared("divider")
        # 创建内容并布局...
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


---

如需扩展：`auto_wrap.py` 可直接在生成代码中用于 Text/Tex 自动换行（贪心控宽、支持中英文混排）。
