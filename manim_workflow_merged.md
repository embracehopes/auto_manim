# Manim 自动化视频生成指南（整合版）

> **整合说明**：本文件合并自 `auto_workflow.md`、`auto_manim_complete_workflow.md`、`manim_prompts_guide.md`，内容只增不减并重新分类整理。

---

## 版本与来源

- `auto_workflow.md`（v1.0，2025-12-19）
- `auto_manim_complete_workflow.md`（v2.0，2025-12-20）
- `manim_prompts_guide.md`

---

## 一、工作流总览

> **工作流概述**：AI 生成文稿 → 配音网站生成音频 → AI 根据文稿时间戳生成 Manim 代码 → 视频剪辑（积累常用音效）

> **核心架构**：`题目输入 → AI-1 产出 JSON（结构化时间轴） → AI-2 产出 ManimGL 代码 → 渲染视频 → 剪辑配音`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Manim 自动化视频生成流程                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────┐    ┌───────────────┐    ┌───────────────┐    ┌─────────────┐ │
│   │  题目   │ →  │   AI-1        │ →  │   AI-2        │ →  │  渲染/剪辑  │ │
│   │ (输入)  │    │ (JSON 生成器) │    │ (代码生成器)  │    │  (输出)     │ │
│   └─────────┘    └───────────────┘    └───────────────┘    └─────────────┘ │
│        │                 │                    │                    │        │
│        ▼                 ▼                    ▼                    ▼        │
│   ? 题目文本        ? 结构化时间轴       ? ManimGL 代码      ? .mp4 视频    │
│   ? 要点大纲        ? 旁白 + 时间戳      ? 可直接运行        ? 配音 + 音效  │
│   ? 参考视频        ? 画面驱动字段       ? 按时间轴对齐                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 为什么要分两个 AI？

| 对比项 | 单 AI 一步到位 | 双 AI 分工协作 |
|--------|---------------|---------------|
| **复杂度** | 同时处理语义、时序、动画细节 | 各司其职，职责清晰 |
| **稳定性** | 容易跑偏或漏掉细节 | 质量稳定一个数量级 |
| **可调试** | JSON 隐含在思考过程中 | JSON 可人工检查/修改 |
| **可复用** | 每次都要重新理解 | JSON 可存档、批量生成 |

---

## 二、AI 生成文稿与时间戳编排

### 2.1 AI 生成文稿

#### 途径一：洗稿已有视频

- **素材来源**：不限于 Manim 领域的视频
- **操作方式**：结构复刻 + 内容重写（详见第七节）

#### 途径二：根据题目自动编排

- AI 根据题目自动编排文稿时间戳
- **时间戳格式**：包含时间起始和结束
- **粒度要求**：一句话一个时间戳

### 2.2 AI-1 输入来源

| 来源 | 描述 | 处理方式 |
|------|------|----------|
| **题目自编** | 给 AI 一个题目/知识点 | 直接生成时间轴 |
| **洗稿复刻** | 已有视频/PPT | 解析 → 重写 → 生成时间轴 |

### 2.3 AI-1 的职责

AI-1 **只负责**产出结构化 JSON，包含：

- 旁白文本（narration）
- 时间戳（start/end）
- 屏幕文字（screen_text）
- 公式内容（latex）
- 视觉动作类型（visual_action）
- 场景编号与段落（scene_id/section）


### 2.5 一句一镜头的“可视化字段”

每句除旁白外，必须同时给出：

| 字段 | 说明 |
|------|------|
| `screen_text` | 屏幕显示文字（可为空） |
| `latex` | 若有公式，用 LaTeX；无则空 |
| `visual_action` | 从限定集合里选择 |

**`visual_action` 限定集合**：
- `标题` / `定义` / `示意图` / `推导` / `例题` / `强调` / `小结` / `转场`

> 这些字段直接驱动后续 Manim 生成，避免"只给旁白，画面靠猜"。

### 2.6 分段与总时长约束

- 输出必须标注：
  - `section`：`intro` / `middle` / `outro`
  - `scene_id`：如 `S1, S2, ...`
- 末尾给出 `TOTAL_DURATION`
- 保证总时长落在目标范围（60–120s）

> **关键点**：你真正需要的是"带结构的时间轴"，而不只是"旁白 + 时间"。

---

## 三、AI-2 生成 ManimGL 代码

### 3.1 AI-2 的职责

AI-2 **只负责**把 JSON 翻译成 ManimGL 代码，包含：

- 严格按时间戳对齐动画
- 根据 `visual_action` 选择动画组合
- 代码可直接运行
- 统一样式与可维护性

### 3.2 visual_action 动画映射表

| visual_action | 动画组合 | 常用 API |
|---------------|----------|----------|
| **标题** | 写入 + 下划线 | `Write(title)` + `Underline` |
| **定义** | 写入 + 框选 | `Write(text)` + `SurroundingRectangle` |
| **示意图** | 创建 + 高亮 | `ShowCreation(fig)` + `FlashAround` |
| **推导** | 分行写入 + 变换 | `TransformMatchingTex` / `Write` |
| **例题** | 写入 + 框选 | `Write` + `SurroundingRectangle` |
| **强调** | 指示 + 闪烁 | `Indicate` / `FlashAround` |
| **小结** | 渐入 + 列表 | `FadeIn` + `VGroup` |
| **转场** | 淡出全部 | `FadeOut(*self.mobjects)` |

---

## 四、JSON Schema

### 4.1 建议 JSON Schema（最小够用版）

```json
{
  "meta": {
    "title": "竖版视频标题",
    "resolution": "1080x1920",
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
    }
  ]
}
```

### 4.2 字段动画说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `meta.title` | string | 视频标题 |
| `meta.resolution` | string | 分辨率 |
| `timeline[].scene_id` | string | 场景编号 |
| `timeline[].section` | string | 段落类型：intro/middle/outro |
| `timeline[].start` | number | 起始时间（秒） |
| `timeline[].end` | number | 结束时间（秒） |
| `timeline[].narration` | string | 旁白文本 |
| `timeline[].screen_text` | string | 屏幕显示文字 |
| `timeline[].latex` | string | LaTeX 公式 |
| `timeline[].visual_action` | string | 视觉动作类型 |

### 4.3 完整 Schema

```json
{
  "meta": {
    "title": "视频标题",
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
        {
          "id": "title_main",
          "type": "Text",
          "content": "一个例子理解XXX",
          "position": "UP",
          "style": "title"
        }
      ],
      "animations": [
        {
          "type": "Write",
          "target": "title_main",
          "run_time": 2.0,
          "rate_func": "smooth"
        }
      ]
    },
    {
      "scene_id": "PAUSE",
      "section": "intro",
      "start": 3.2,
      "end": 4.0,
      "narration": "",
      "screen_text": "",
      "latex": "",
      "visual_action": "转场",
      "note": "段落停顿"
    }
  ],
  "total_duration": 120.0
}
```

### 4.4 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `meta.title` | string | ✅ | 视频标题 |
| `meta.resolution` | string | ✅ | 分辨率（如 1080x1920 竖版） |
| `meta.target_duration` | array | ✅ | 目标时长范围 [min, max] |
| `meta.style` | object | ✅ | 全局样式配置 |
| `timeline[].scene_id` | string | ✅ | 场景编号（S1, S2...或 PAUSE） |
| `timeline[].section` | string | ✅ | 段落：intro/middle/outro |
| `timeline[].start` | number | ✅ | 起始时间（秒） |
| `timeline[].end` | number | ✅ | 结束时间（秒） |
| `timeline[].narration` | string | ✅ | 旁白文本 |
| `timeline[].screen_text` | string | ✅ | 屏幕显示文字 |
| `timeline[].latex` | string | ✅ | LaTeX 公式 |
| `timeline[].visual_action` | string | ✅ | 视觉动作类型 |
| `timeline[].objects` | array | ✅ | 对象列表（高级用法） |
| `timeline[].animations` | array | ✅ | 动画列表（高级用法） |
| `total_duration` | number | ✅ | 总时长 |

---

## 五、代码生成规范与额外要求（AI-2 必读）

### 5.1 时间轴对齐规则

```python
# 时间轴驱动器（必须实现）
t = 0  # 全局时间指针

def play_t(self, *anims, rt=1):
    """播放动画并更新时间指针"""
    self.play(*anims, run_time=rt, rate_func=smooth)
    self.t += rt

def wait_t(self, dt):
    """等待并更新时间指针"""
    self.wait(dt)
    self.t += dt

def wait_until(self, target):
    """等待到目标时间点"""
    if target > self.t:
        self.wait_t(target - self.t)
```

### 5.2 代码组织规范

```python
from manimlib import *

class AutoVideo(InteractiveScene):
    # ========== 常量区 ==========
    TITLE_POS = UP * 2.5       # 标题位置
    BODY_POS = ORIGIN          # 正文位置
    TITLE_SCALE = 1.2          # 标题缩放
    BODY_SCALE = 0.9           # 正文缩放
    
    # ========== 样式配置 ==========
    FONT_CN = "STKaiti"
    FONT_EN = "Arial"
    PRIMARY_COLOR = WHITE
    ACCENT_COLOR = RED
    
    def construct(self):
        """主流程调度"""
        self.t = 0  # 时间指针
        self.setup_scene()
        self.phase1_intro()
        self.phase2_main()
        self.phase3_outro()
    
    def setup_scene(self):
        """初始化场景"""
        pass
    
    def phase1_intro(self):
        """阶段1：开场"""
        # 1. 创建对象
        title = Text("标题", font=self.FONT_CN)
        title.move_to(self.TITLE_POS)
        
        # 2. 播放动画
        self.play_t(Write(title), rt=2)
        self.wait_until(3.2)
        
        # 3. 清理/保留对象
        self.title = title  # 保留跨阶段对象
```

### 5.3 必须遵守的规则

| 规则 | 说明 |
|------|------|
| **Tex 禁用 `\\div`** | 用 `÷` 替代，如 `Tex("6÷2=3")` |
| **Text 使用 STKaiti** | `Text("文字", font="STKaiti")` |
| **使用 Transform 衔接** | 相似物体间用 `Transform` 而非重复 `Write` |
| **阶段独立可调试** | 每个 `phaseN_xxx()` 可独立运行 |
| **统一清理对象** | 阶段末尾清理临时对象，保留共享对象 |
| **遮挡关系** | 后 `self.add` 的在上层 |
| **默认动画参数** | `rate_func=smooth, run_time=2` |

### 5.4 自检输出

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

### 5.5 代码生成额外要求

根据下面解题过程，上传题目图片和我的要求，参考E:\auto_manim\voice_test\odd_function_demo.py文件，创建对应的 manimgl 竖版动画代码文件，使用autoscene，只创建一个场景即可。

#### 要求

1. **Tex 中禁用 `\\div`**，用 `÷` 替代，例如：`div = Tex("6÷2=3")`，涉及到数字和字母的都一律使用 Tex，只涉及到中文的都一律使用 Text

2. **text 中使用 text2color 给部分字体上色**，字体统一使用 STKaiti

3. **使用 Transform 衔接相似物体**

4. **每阶段开头检查机制**，允许对我在注释其中某个阶段后对每一个阶段单独调试

5. **统一清理每个阶段的对象**，保留跨阶段共享对象，用于transform衔接

6. **遮挡关系取决于 self.add 的顺序**：后 add 的对象 → 在上层 → 遮挡先 add 的对象

7. **代码组织**：
   - 类开头定义常量区（每个物体都要设置一个可调试位置数据入口和对应的大小缩放接口便于调试，带注释）
   - `construct()` 只做流程调度，调用 `setup_scene()` 和各 phase 方法
   - 每阶段封装为 `phaseN_xxx()` 独立方法
   - 每个 `phaseN_xxx()` 前部分创建物体和设置位置，末尾统一部分进行动画

8. **self.play() 中都设置为 `rate_func=smooth, run_time=2`**
9. **axes 坐标轴参数设置中，要加入"include_ticks": False，其次就是x_range/y_range=width/height，要保证比值相等，即xy方向上的单位长度需要一致
例如：
        ax2 = Axes(
            x_range=[-2, 5, 1],
            y_range=[-2, 5, 1],
            width=7,
            height=7,
            axis_config={"stroke_width": 1.5, 
                        "color": BLUE,
                        "include_tip": False，
                        "include_ticks": False},
        )
10.需要配音合理，字幕和配音同步，留有合理的气口时间0.5s。
11.向量上使用长箭头来表示\overrightarrow{...}。
12.在开场的时候，要配音，动画，音效同时出现。其次在配音讲解的过程，要indicate相应的部分，或者配有相应的动画，配音时间段一定不能静止在那里，除了气口时间。
13.DecimalNumber
排版要求：
1. 最上方标题（说明题目来源或者时所属专题，只用一行），其次就是使用Tex来排版的题目，然后就是可视化区域，再然后就是证明过程，最后是字幕（通过autoscene自带的方法使用）
例如：
source = Text(
            "【高考真题·函数综合】",
            font="STKaiti",
            font_size=self.SOURCE_FONT_SIZE,
            color=GREY
        ).move_to(UP * (self.TITLE_Y + 0.3))
2. 可视化区域，一定要使用更新器来展示动态过程，对应字体的更新要使用DecimalNumber的api，可视化区域中的标注信息需要使用彩色背景突出显示
3. 题目要使用Tex，来排版
4. 解析推导区域不能与字幕重叠，解析推导区域的最后一行一定要控制在字幕的上方，允许与图像可视化区域重叠，使用自适应调高，就是测算最后一行的推导解析的文本的bottom的y值和字幕的top的y值的插值的逻辑来自适应调整，重叠的时候移动的时候多加个0.2的buff，没有重叠的话放到图像可视化区域底部和字幕顶部的中间
5. 公式推导如果上下具有联系的部分，要对上一行的公式对象使用TransformMatchingShapes的api变换到下一行的公式对象，如果是第一行或者没有联系的部分则使用Write的api
6. 标题题目和分割线条，推导过程，字幕，字幕背景都要fix_in_frame吗，可视化的标签信息需要add_fixed_annotation
### 竖版布局自适应规则（必须遵守）

#### 屏幕宽度适配
```python
# 竖版安全宽度常量
SCREEN_WIDTH = 27/4  # 竖版 9:16 的安全宽度（留边距）

# 所有文本/公式组创建后必须检查宽度，超出则缩放
if mobject.get_width() > SCREEN_WIDTH:
    mobject.stretch_to_fit_width(SCREEN_WIDTH*0.95, stretch=False)
```



#### 可视化区域必须可见
- **可视化区域和解题过程必须同屏显示**，采用以下任一布局：
  - **上下布局**：可视化在上，解题在下
- **可视化区域不能被解题过程遮挡或挤出屏幕**
- 解题步骤过多时，分批显示（FadeOut上一批，FadeIn下一批）

#### 题目排版规则
- 长题目必须换行或缩放：`scale_to_fit_width(SCREEN_WIDTH)`
- 使用 `VGroup().arrange(DOWN, aligned_edge=LEFT)` 多行排列
- 中文用 `Text(font="STKaiti")`，公式用 `Tex`，混排用 `VGroup` 拼接

#### 解题步骤布局
- 每个小问的解题步骤要紧凑排列（`buff=0.12~0.2`）
- 切换小问时 `FadeOut` 上一问的步骤，避免堆叠
- 最终答案需要 `Indicate` 高亮强调
---

## ⚠️ 配音与字幕分离（重要）

`speak()` 支持**配音+字幕+高亮**（统一 API）：
- `text`: 配音文稿（TTS 朗读，口语化中文）
- `subtitle`: 字幕文本（屏幕显示，可用符号）
- `targets`: 要高亮的对象列表（可选）

> ⚠️ **注意**：原 `speak_with_highlight` 已弃用，使用 `speak(..., targets=[obj])` 替代

### 转换规则

| 类型 | 配音（text） | 字幕（subtitle） |
|------|-------------|-----------------|
| 负号 | `f 负 2 等于 负 4` | `f(-2) = -4` |
| 等号 | `a 等于 5` | `a = 5` |
| 坐标 | `坐标 2 4` | `(2, 4)` |
| 小于 | `x 小于 0` | `x < 0` |
| 平方 | `x 平方` | `x²` |

### 使用示例

```python
# 方式1: 配音和字幕相同（简单场景）
self.speak("欢迎观看本视频")

# 方式2: 配音和字幕分离（推荐用于数学内容）
self.speak(
    text="由 f 2 等于 4",           # TTS 读这个
    subtitle="由 f(2) = 4",          # 屏幕显示这个
)

# 复杂数学表达
self.speak(
    text="f 负 2 等于 负 4",
    subtitle="f(-2) = -4",
    color_map={"-4": YELLOW}
)

# 带高亮的配音（使用 targets 参数）
self.speak(
    text="利用奇函数性质，f 负 2 等于 负 4",
    subtitle="利用奇函数性质，f(-2) = -4",
    targets=[formula],  # 高亮对象列表
)
```

---
## 六、提示词模板库

### 6.1 AI-1 提示词：生成结构化 JSON

```markdown
你是短视频脚本与时间轴编排器。请基于我给出的主题与要点，生成「旁白 + 时间戳 + 画面驱动字段」的 JSON。

## 规则

1. **字速标准**
   - intro：5 字/秒
   - middle：4.5 字/秒  
   - outro：5 字/秒

2. **时间格式**
   - 精度：0.1s，格式为浮点（如 12.3）
   - 严格递增且不重叠

3. **停顿规则**
   - 句末：0.2–0.4s
   - 转场：0.6–1.0s（用单独事件标注 `visual_action="转场"`）

4. **必须字段**
   每句必须包含：
   - `scene_id`：场景编号（S1, S2...）
   - `section`：段落类型（intro/middle/outro）
   - `start`：起始时间
   - `end`：结束时间
   - `narration`：旁白文本
   - `screen_text`：屏幕显示文字
   - `latex`：LaTeX 公式（无则为空）
   - `visual_action`：从 [标题/定义/示意图/推导/例题/强调/小结/转场] 中选择

5. **时长控制**
   总时长控制在【60, 90】秒，通过调整停顿实现

## 输出要求
仅输出 JSON，不要额外解释

## 主题与要点
<在此粘贴你的题目或大纲>
```

### 6.2 AI-2 提示词：生成 ManimGL 代码

```markdown
你是 ManimGL（manimlib）动画工程师。请将我提供的 timeline JSON 转为可运行的 ManimGL 代码。

## 规则

1. **基础要求**
   - 使用 `from manimlib import *`
   - Scene 类名为 `AutoVideo`
   - 继承 `InteractiveScene`

2. **时间对齐**
   - 严格按 `start/end` 对齐每条事件
   - 实现 `play_t()`, `wait_t()`, `wait_until()` 三个时间驱动方法
   - 误差 ≤ 0.2s

3. **动画映射**
   - 标题 → `Write` + `Underline`
   - 定义 → `Write` + `SurroundingRectangle`
   - 推导 → `TransformMatchingTex` / 分行 `Write`
   - 强调 → `Indicate` / `FlashAround`
   - 转场 → `FadeOut(*self.mobjects)`

4. **代码规范**
   - Tex 禁用 `\\div`，用 `÷` 替代
   - Text 使用 `font="STKaiti"`
   - 相似物体用 `Transform` 衔接
   - 每阶段封装为 `phaseN_xxx()` 方法
   - `self.play()` 默认 `rate_func=smooth, run_time=2`

5. **代码结构**
   - 类开头定义常量区（位置、缩放、颜色等）
   - `construct()` 只做流程调度
   - 包含渲染前自检打印

## 输出要求
仅输出代码，不要额外解释

## JSON
<在此粘贴 AI-1 生成的 JSON>
```

### 6.3 生成"结构化时间戳文稿"的提示词（上游）

```markdown
你是短视频脚本与时间轴编排器。请基于我给出的主题与要点，生成"旁白 + 时间戳 + 画面驱动字段"的 JSON。

规则：
1）intro 按 5 字/秒，middle 按 4.5 字/秒，outro 按 5 字/秒估时；
2）时间精度 0.1s，格式秒为浮点（如 12.3）；严格递增不重叠；
3）句末默认加 0.2–0.4s 停顿；转场加 0.6–1.0s，并用单独事件标注 `visual_action="转场"`；
4）每句必须包含：`narration, screen_text, latex, visual_action, scene_id, section, start, end`；
5）总时长控制在【X, Y】秒；优先通过调整停顿实现，不要硬改语义；

输出：仅输出 JSON，不要输出解释文字。

主题与要点：<粘贴这里>
```

### 6.4 生成"ManimGL 代码"的提示词（下游）

```markdown
你是 ManimGL（manimlib）动画工程师。请将我提供的 timeline JSON 转为可运行的 ManimGL 代码：

* 使用 `from manimlib import *`，Scene 类名为 `AutoVideo`；
* 严格按 `start/end` 对齐：每条事件在其时间窗内完成动画，不足用 `self.wait()` 补齐；
* 依据 `visual_action` 使用固定动画模板（标题/定义/示意图/推导/例题/强调/小结/转场）；
* 文本用 `Text`，公式用 `MathTex`；尽量 `Transform` 复用对象；
* 统一样式：字号、颜色、边距、对齐；
* 代码包含：配置区、事件调度器（按时间轴顺序播放）、必要的自检打印；

输出：仅输出代码，不要解释。

JSON：<粘贴这里>
```

### 6.5 视频/PPT 解析提示词（洗稿用）

```markdown
请对我提供的视频/PPT 进行内容解析，输出可交给代码生成 AI 的 JSON 时间轴。

## 输出内容

1. **分镜脚本**（精度 1s）
   - Shot 编号
   - 时间范围
   - 画面状态描述
   - 核心变化

2. **场景对象清单**
   - 变量名建议
   - 类型（Text/Tex/MathTex/Arrow/Circle...）
   - 样式参数
   - 布局参数

3. **动画事件时间轴**
   - ManimGL 动作词
   - 参数（run_time, rate_func, lag_ratio...）
   - 同步关系

4. **文本/公式逐字稿**（必须精确）

5. **最终 JSON 输出**
   按本工作流的 Schema 格式输出
```

---

## 七、视频版本解析要求

### 目标

请你对我提供的视频进行内容解析与可复现抽象，输出一份"可直接交给另一个 AI 生成 ManimGL 动画代码"的高精度提示词包。解析需覆盖画面元素、分镜结构、动画顺序、时间节奏与文字/公式细节，确保在 ManimGL 中能够被工程化复刻（允许少量视觉近似，但信息结构与时序必须一致）。

### 适用环境

- 动画引擎：ManimGL（3Blue1Brown 体系）

### 你需要输出的内容（必须逐项给出）

#### 1) 分镜脚本（Shot List，带时间戳）

对视频按镜头/段落切分，至少输出到 1s 精度：

- Shot 编号
- 时间范围（如 00:12–00:18）
- 该镜头的"画面状态描述"（哪些对象在画面上、布局、相对位置）
- 该镜头的"核心变化"（新增/消失/移动/变形/颜色变化/缩放/旋转/相机运动）

#### 2) 场景对象清单（Mobject 级别清单）

以"可写成代码"的粒度列出对象，至少包括：

- 对象名称（建议给代码变量名，例如 title, axes, curve, label_1）
- 对象类型（Text/Tex/MathTex/Line/Arrow/Circle/Polygon/NumberPlane/Axes/SVGMobject/ImageMobject 等）
- 样式参数：颜色（hex/RGB/Manim color 常量）、线宽、填充透明度、字体、字号、描边、发光等
- 布局参数：位置（相对屏幕/相对其他对象）、对齐方式（to_edge/next_to/align_to）、缩放比例
- 若存在图像/图标：列出素材文件名与来源（无素材则给占位方案）

#### 3) 动画事件时间轴（ManimGL 动作词 + 参数）

按时间顺序列出每个动作，要求能够直接映射到 ManimGL API。每条事件至少包含：

- 发生时间或相对顺序
- 动作类型（如 ShowCreation, Write, FadeIn, FadeOut, Transform, ReplacementTransform, MoveToTarget, ApplyMethod, GrowArrow, Uncreate 等）
- 动画参数：run_time、rate_func（smooth/linear/there_and_back 等）、lag_ratio（如有）、path_arc（如有）
- 同步关系：哪些动画 self.play(...) 同时发生

#### 4) 相机与构图（若视频存在镜头运动）

若视频包含缩放/平移/跟随/摇移，请输出：

- Camera frame 的初始状态（位置、缩放）
- 每次相机运动的起止时间、目标、缓动
- 是否需要使用 `self.play(self.camera.frame.animate.reorient()）`（ManimGL 习惯写法）

#### 5) 文本/旁白/字幕/公式逐字稿（必须精确）

- 按时间戳列出每一段字幕/标题/公式的逐字内容
- 明确使用 Text 还是 Tex/MathTex（需要 LaTeX 的请给出可编译版本）
- 若有高亮/变色/逐词出现：标注对应文字片段与动画方式
- 若有旁白但无字幕：尽可能根据画面推断并标注"不确定内容"，并给替代处理方案（如用简短字幕概括）

#### 6) 全局风格规范（Style Guide）

输出一个统一的风格块，供代码生成 AI 直接设置：

- 字体选择（中英文字体策略）、字号层级（标题/正文/注释）
- 线条粗细层级、透明度规范

#### 7) 代码生成 AI 的"总 Prompt"（最终交付物）

在所有分析之后，请再输出一段可直接复制给代码生成 AI 的完整提示词，要求：

- 明确：必须用 ManimGL
- 要求：代码注释清晰，关键参数可配置

### 解析策略要求（保证准确性）

- 优先保证：信息结构、相对布局、出现顺序、关键变换 的一致性
- 对于难以辨认的细节：必须显式标注"无法确定/近似处理"，并给出 1–2 个可选实现方案

---

## 八、PPT 版本解析要求

### 任务

PPT 内容解析与可复现抽象 → 输出给代码生成 AI 的 ManimGL 高精度提示词包

我将上传一个 .pptx。请你逐页解析该 PPT 的内容细节与呈现逻辑，抽象出可在 ManimGL（3Blue1Brown 体系） 中工程化复刻的动画方案。允许少量视觉近似，但信息结构、相对布局、出现顺序、关键变换与节奏必须一致。

### 适用环境

- 动画引擎：ManimGL（3b1b）
- 字体策略：中文{思源黑体/微软雅黑等}，英文{CMU Serif/Arial 等}（若我未指定，请你给出稳妥默认与替代方案）

### 你必须输出（逐项给出）

#### 1) 页级分镜脚本（Slide Shot List，带时间戳或相对时序）

- Slide 编号与标题（若无标题则用"Slide N"）
- 每一步的画面状态（屏幕上有哪些对象、布局、相对位置）
- 每一步的核心变化（新增/消失/移动/变形/颜色变化/缩放/旋转/镜头运动）

#### 2) 场景对象清单（Mobject 级别清单，按"全局复用 + 每页新增"组织）

对每个对象给出：

- 代码变量名建议（如 title, axes, vec_v_ship, label_tmin）
- 类型（Text/Tex/MathTex/Line/Arrow/Polygon/ImageMobject/SVGMobject 等）
- 样式参数（颜色 hex、线宽、填充/透明度、字体、字号、描边/发光）
- 布局参数（相对屏幕位置、对齐方式 to_edge/next_to/align_to、缩放比例）

#### 3) 动画事件时间轴（ManimGL 动作词 + 参数）

按顺序列出每条事件，至少包含：

- 时刻（绝对秒或相对顺序，如 S3-B2-Event4）
- 动作（Write/FadeIn/FadeOut/Transform/ReplacementTransform/ShowCreation/Uncreate/ApplyMethod 等）
- 参数（run_time、rate_func、lag_ratio、path_arc 等）
- 并行动画关系（哪些写在同一个 self.play(...)）

#### 4) 镜头与构图（若需要 camera frame）

- 初始 frame 位置与缩放
- 每次镜头运动的起止、目标与缓动
- 是否使用 `self.play(self.camera.frame.animate.reorient()）` 的推荐写法

#### 5) 文本/公式逐字稿（必须精确）

- 按页/按 Build 给出每段文字、每条公式的逐字内容
- 若存在逐词出现/高亮变色/下划线框选：标注具体片段与对应动画

#### 6) 全局风格规范（Style Guide）

- 字号层级（标题/正文/注释/角标）
- 颜色与线宽层级、透明度规范
- 对齐栅格与留白规则（保证画面不挤）

#### 7) 给"代码生成 AI"的最终总 Prompt（可直接粘贴）

- 强制：ManimGL

---

## 九、题目图片：版本解析要求
0) 输入约束（你提供图片时建议附带，但不是必须）

图片类型：截图/照片/扫描件/拼接图

若有：题目来源（章节/编号/课程）、期望解法风格（考试版/讲解版/竞赛版）

若有：目标时长（例如 60s / 3min / 8min），或目标讲解深度（只讲关键步骤/讲完整推导）

你必须输出的内容（逐项给出）
1) 题面信息抽取与可靠性标注（必须）

对图片做“结构化 OCR + 版面理解”，输出：

题目逐字稿（原题面）

分块输出：标题/题干/小问(1)(2)(3)/已知条件/图形标注/表格/注释

对每一块给出：

content：逐字文本（公式用可编译 LaTeX）

type：Text / MathTex / 纯符号 / 图形标注

confidence：高/中/低（低则必须给替代方案）

uncertain_spans：不确定片段用 【?】 标记

图形/示意图解析（若存在）

列出所有几何对象或示意元素：点、线段、角标、坐标轴、曲线、阴影区域、箭头、表格列标题等

若无法完全确定，必须写明：

“无法确定的原因”（遮挡/像素/倾斜/光照）

近似方案 A/B（例如：用简化示意图替代；或直接保留原图并框选关键区域）

版面布局摘要（用于复刻相对位置）

用“屏幕归一化坐标”描述每个块的位置（不要求像素级，但要可复刻）

建议格式：

block_name: bbox=(x0,y0,x1,y1)，x,y ∈ [0,1]，以屏幕左下为 (0,0)

目标：保证“题目内容不会抄错/漏条件/漏符号”。如果某处低置信度，你必须在输出里显式标注并给两套可执行方案。

2) 可复刻的“题目重排版”版本（必须）

输出一份“适合上屏讲解”的重排版题面（不是照搬图片布局，而是板书/课件风格），要求：

标题（可选）：如“例题：xxx”

题干：按语义断行，避免一行过长

公式：全部给出可编译 LaTeX（MathTex）

小问：编号统一（(1)(2)(3) 或 a,b,c）

若原图有图：给出图的复刻版本或“保留原图 + 框选 + 标注”的替代策略

输出时必须同时提供：

DisplayVersion：最终上屏文本/公式（可直接变成 Text/Tex/MathTex）

SourceMapping：每一行对应原图哪个信息块（便于校对）

3) 分镜脚本（Shot List，带时间戳，必须）

将“题目图片 → 题面重排版 → 解题过程 → 总结”切分镜头，至少到 1s 精度。每个 Shot 必须包含：

Shot 编号

时间范围（例如 00:00–00:06）

画面状态描述（对象有哪些、相对位置）

核心变化（出现/消失/变形/移动/高亮/框选/相机运动）

讲解意图（这一镜头讲什么，为什么需要这个变化）

推荐镜头模板（可按需要删改）：

开场：展示原题图片（或题面重排版标题）

题面信息聚焦：框选条件/问法/关键图形

题面净化：Transform 成清爽排版版本

解题主线：逐步推导（每步一个视觉“落点”）

结果汇总：框出最终答案 + 条件回扣（可选：检验/讨论）

4) 场景对象清单（Mobject 级别清单，必须）

以“可写成代码”的粒度列出对象，要求包含变量名建议、类型、样式、布局与复用关系：

全局对象（复用）：title、subtitle、watermark、page_frame、step_index、highlight_box 等

题面对象：

img_problem（ImageMobject，原题图，可选）

stmt_group（重排版题面 VGroup：Text/Tex/MathTex）

fig_group（几何/示意图对象集合，若有）

解题对象：

eq_1, eq_2, ...（每一步公式）

note_1, note_2, ...（解释性短句）

mark_assumption / mark_key（框选、下划线、箭头、颜色高亮）

每个对象必须给：

类型：Text/Tex/MathTex/Line/Arrow/SurroundingRectangle/Brace/Axes/NumberPlane/ImageMobject 等

样式：颜色（hex 或 Manim 常量）、stroke_width、fill_opacity、font、font_size、buff

布局：to_edge/next_to/align_to/shift/scale 的相对描述

复用说明：哪些对象只创建一次，哪些是 Transform 的目标

5) 动画事件时间轴（ManimGL 动作词 + 参数，必须）

按顺序列出可直接映射到 ManimGL 的事件。每条事件必须包含：

时间点（绝对秒或相对序号）

动作类型：ShowCreation / FadeIn / FadeOut / Write / Transform / ReplacementTransform / Indicate / Wiggle / Flash / ApplyMethod / MoveToTarget / Uncreate 等

参数：run_time、rate_func、lag_ratio、path_arc（如有）

并行动画：同一个 self.play(...) 里有哪些动画同时发生

与字幕同步：该事件对应哪句字幕（subtitle_id）

要求：

对“题面重排版”必须指定：是 TransformMatchingTex / ReplacementTransform / FadeTransformPieces 还是简单 Fade。

对“推导链”必须说明：新公式是 Write 还是由旧公式 Transform 而来（减少跳变）。

6) 相机与构图（若需要，必须）

若你希望“框选题面细节/放大图形/推导区分屏”，则必须输出：

初始 camera frame：位置、缩放（scale 或 width/height 的相对说明）

每次镜头运动：起止时间、目标区域、缓动函数

推荐写法（ManimGL）：self.play(self.camera.frame.animate.scale(...).move_to(...), ...)

是否需要“跟随对象”：例如跟随当前推导行、或在图形局部放大

7) 字幕文稿与旁白稿要求（强制：用于你的工作流）

你要的工作流核心是“一句话一个时间戳 + 可驱动字幕 Transform/Write”。因此本部分必须严格结构化输出：

7.1 字幕清单格式（必须）

以表格或 YAML/JSON 形式输出，每条字幕包含：

id：S001, S002, ...

t_start：起始时间（mm:ss 或秒）

t_end：结束时间

text：一句话字幕（中文为主，允许夹公式）

mode：title / subtitle / narration / equation_hint

on_screen：是否同步上屏（true/false）

action_hint：建议动作

第一条：Write

后续：Transform 上一句 → 下一句

anchor：字幕摆放策略（bottom_center / top_left 等）

pace_note：语速说明（快/中/慢）

7.2 字幕时长生成规则（必须写明并执行）

如果用户未提供时长，你必须按可复刻规则自动分配时间：

开场字幕：5 字/秒（或等效英文 12–15 chars/s）

正文讲解：4.5 字/秒

公式/符号密集句：按“有效字数”折算

建议：一个 LaTeX 公式块按 8–12 个字等效（取中值 10，或你自行解释采用的换算）

每句最短时长：1.6s（避免闪烁）

句与句之间可留 0.1–0.2s 缓冲（若你工作流需要严格无缝也可为 0）

你必须输出：

每句“字数估计/折算字数”

每句由规则推导的时长

最终总时长

7.3 字幕内容规范（必须）

一句只表达一个动作意图：读题、提取条件、设变量、列方程、代入、化简、得结论、检验等

避免长句：超过 22–26 字建议拆分两句（各自时间戳）

公式建议“口语化 + 局部上屏公式”配合：

旁白字幕：解释逻辑

上屏公式：MathTex 逐步出现

若图片内容有不确定处：字幕中必须显式写 【此处题面不清晰：…】，并给替代版本字幕

8) 解题内容输出粒度要求（图片题通常需要）

为确保动画“信息密度可控”，你必须提供两套解题粒度（供我选其一；若我没选，你默认考试版）：

考试版（默认）：步骤少但逻辑闭合；每步落到一个等式/结论

讲解版（可选）：补充关键解释、常见坑、条件为什么要这样用

并且要求：

每一步对应一个 Step 编号：Step1/Step2/...

每个 Step 绑定：

equation_tex（可为空）

explain_text（一句字幕版本）

visual_action（框选/高亮/箭头指向/变色）

9) 全局风格规范（Style Guide，必须）

建议给一套“题目讲解类视频”的稳妥默认值（你也可以按我既有风格调整）：

背景：深色纯色或轻微渐变（避免干扰题面）

字体策略：

中文 Text：思源黑体/微软雅黑（优先可用者）

英文/数字：Arial 或与中文同族；公式用 LaTeX 默认

字号层级（示例，可给具体数值）：

标题 48–56

正文 34–40

注释 28–32

角标/编号 24–28

线宽层级：主线 4，辅助线 2–3，高亮框 6

高亮色策略：只用 1–2 个强调色；“关键条件/关键等式/最终答案”颜色一致

留白规则：推导区不超过屏幕高度 70%，避免顶到边缘

10) 给“代码生成 AI”的最终总 Prompt（必须，可直接粘贴）

在输出最后，你必须再给一段“总 Prompt”，其结构固定为：

强制：ManimGL（3b1b 系）

场景类：建议使用 InteractiveScene 或用户自定义 AutoScene

必须实现：

原题图导入（可选开关）

题面重排版对象生成

Shot List 严格按时间轴执行

字幕系统：第一句 Write，其余 Transform（与时间戳绑定）

关键对象变量命名与分组（便于复用 TransformMatchingTex）

关键参数可配置（字体、字号、颜色、run_time、语速）

并附上：

“字幕数据结构”建议（list[dict] 或 YAML）

“时间控制策略”：按 t_start/t_end 驱动 wait() 或自定义 time tracker

若有不确定内容：实现 A/B 两套开关（例如 USE_ORIGINAL_IMAGE=True / False）

解析策略要求（针对图片题，额外补充）

任何“可能抄错一个符号就会变题”的地方（±、上下标、积分上下限、向量箭头、集合符号、开闭区间）必须做 confidence 标注

若图中有手写：必须提供“手写转标准数学符号”的映射表（例如：像 v 的到底是 ν 还是 v）

若图片含多题：必须先拆分题号，再分别输出上述 1–10 项；最后提供一个“总目录镜头”可选
### 9.1 视频洗稿流程

```
原视频 → AI 解析分镜 → 提取结构 → 重写内容 → 生成 JSON → AI-2 生成代码
```

### 9.2 PPT 复刻流程

```
PPT 上传 → 逐页解析 → 提取文本/公式/布局 → 生成 JSON → AI-2 生成代码
```

### 9.3 特征提取清单

当需要让 AI 生成「同质化」代码时，提取以下特征：

| 类别 | 特征项 |
|------|--------|
| **字体** | Text 使用 STKaiti，公式用默认 |
| **动画衔接** | 相似物体用 Transform 而非 FadeOut+FadeIn |
| **代码结构** | 常量区 + construct 调度 + phaseN 方法 |
| **颜色策略** | 默认白色，强调时短暂变红 |
| **时间对齐** | 使用时间驱动器三件套 |

---

## 十、特征提取要求

从这个文件，提取其中的特征，以便我使用这些特征提示词让其他 AI 生成其他差不多的同质化的代码。

做一个 md 文档，尽量简洁。特征例如：
- text 中使用 STKaiti 字体
- 前后两个场景有类似的物体变化尽量使用 transform 来衔接
- 等等

---

## 十一、音稿时间戳同步任务

### 任务目标

1. 根据文稿时间戳，Indicate 对应屏幕已有的文本对象，所有显示在屏幕上的文本对象都需要被强调至少一遍
2. 简略屏幕上已有的文本对象的内容，以便字号大一点
3. 调整颜色为白色，只在重点短暂变色
4. 时间轴严格对齐（核心）
5. 最终额外输出一份在保留原版除开文本的其他可视化逻辑基础上的修改版代码文件
6. 动画总时间控制为 126s
7. 加入 `print()` 每一个时间戳的逻辑
8. 尽量少使用 `self.wait()`，只允许在每个独立阶段结束时使用 `self.wait()`，延长其他的物体的变化 run_time 来衔接符合时间戳的规则

### 具体实现

#### 1) 字号更大 + 内容更加简洁

#### 2) 文字颜色策略：默认白色，只在重点短暂变色

- 默认所有文字 WHITE
- 只允许 1 种强调色（建议 RED），用于"重点词/关键结论/关键公式"：
  - 强调持续 2s，然后恢复 WHITE
- 禁止出现大量红字、彩字、连续闪烁

#### 3) 时间轴严格对齐（核心）

不依赖当前散落的 run_time 习惯写法；请实现一个"时间轴驱动器"，保证对应文稿的时间戳。

要求实现以下三个辅助函数（放在 `construct()` 内或作为方法均可）：

- `play_t(..., rt=...)`：调用 `self.play(..., run_time=rt)` 后把 `t += rt`
- `wait_t(dt)`：`self.wait(dt)` 后 `t += dt`
- `wait_until(target)`：若 `target > t` 则 `wait_t(target - t)`

最终与时间戳误差 ≤ 0.2s。

#### 4) 提取音稿和对应的时间戳

提取音稿和对应的时间戳（包括起始和结束时间点），细致一点

#### 5) 时间戳如下


---

## 十二、待办事项

- [ ] 常用音效库整理
- [ ] 配音网站推荐列表
- [ ] 视频剪辑模板
- [ ] ManimGL 代码模板库
- [ ] 常用音效库整理（附 `SoundLibrary` 类）
- [ ] JSON Schema 校验工具
- [ ] 时间轴可视化预览工具

---

*文档版本：整合版*  
*整合日期：2025-12-20*  
*来源：`auto_workflow.md` + `auto_manim_complete_workflow.md` + `manim_prompts_guide.md`*
