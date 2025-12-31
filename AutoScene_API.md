# AutoScene API 文档

> ManimGL 自动化时间轴驱动场景类，专为 AI 辅助视频创作设计

## 目录

1. [快速开始](#快速开始)
2. [核心概念](#核心概念)
3. [语音配音 API](#语音配音-api)
4. [字幕管理 API](#字幕管理-api)
5. [视觉引导 API](#视觉引导-api)
6. [相机控制 API](#相机控制-api)
7. [辉光效果 API](#辉光效果-api)
8. [调试工具 API](#调试工具-api)
9. [完整示例](#完整示例)

---

## 快速开始

### 基本用法

```python
from auto_scene import AutoScene
from manimlib import YELLOW, RED

class MyScene(AutoScene):
    def construct(self):
        # 启用调试模式（可选）
        self.enable_debug(True)
        
        # 方式1: 使用 speak() 自动配音
        self.speak("欢迎观看本视频")
        self.speak("今天我们来学习向量", color_map={"向量": YELLOW})
        
        # 方式2: 使用时间轴批量处理
        timeline = [
            {"start": 0.0, "end": 2.0, "text": "第一句话"},
            {"start": 2.0, "end": 4.0, "text": "第二句话"},
        ]
        self.run_timeline(timeline)
```

### 继承关系

```
manimlib.Scene
    └── AutoScene  # 本类
```

---

## 核心概念

### 类配置常量

| 常量 | 默认值 | 说明 |
|------|--------|------|
| `SUBTITLE_FONT` | `"STKaiti"` | 字幕字体 |
| `SUBTITLE_FONT_SIZE` | `28` | 字幕字号 |
| `SUBTITLE_MAX_CHARS_PER_LINE` | `20` | 每行最大字符数 |
| `DEFAULT_VOICE` | `"zh-CN-XiaoxiaoNeural"` | TTS 默认语音 |
| `VOICE_GAP_DURATION` | `0.5` | 句间气口时长（秒）|

### 时间轴事件格式

```python
event = {
    "start": 0.0,          # 开始时间（秒）
    "end": 2.5,            # 结束时间（秒）
    "text": "字幕文本",     # 显示的文字
    "color_map": {         # 可选：关键词着色
        "关键词": YELLOW,
        "重点": RED
    }
}
```

---

## 语音配音 API

### `speak(text, color_map=None, min_duration=2.0) -> float`

**最常用！** 自动生成配音并显示字幕

```python
# 基础用法
self.speak("这是一段配音文字")

# 带关键词高亮
self.speak("重点是向量加法", color_map={"重点": YELLOW, "向量加法": RED})

# 返回值是实际使用的时长
duration = self.speak("这句话")
```

**参数：**
- `text`: 配音文本
- `color_map`: 关键词着色字典 `{"关键词": 颜色}`
- `min_duration`: 最小显示时长（默认 2.0 秒）

**返回：** 实际使用的时长（秒）

---

### `speak_with_highlight(text, targets=None, color_map=None, min_duration=2.0) -> float`

配音的同时高亮指定对象

```python
formula = Tex("E = mc^2")
self.add(formula)

# 说话时高亮公式
self.speak_with_highlight(
    "这是著名的质能方程",
    targets=[formula],
    color_map={"质能方程": YELLOW}
)
```

---

### `speak_sequence(texts, min_duration=2.0)`

顺序播放多条语音（AI 工作流推荐）

```python
self.speak_sequence([
    "欢迎观看本期视频",
    "今天我们学习向量",
    {"text": "重点是向量加法", "color_map": {"重点": YELLOW}},
])
```

---

### `run_timeline(events, generate_voice=None)`

执行完整时间轴

```python
timeline = [
    {"start": 0.0, "end": 2.5, "text": "第一句"},
    {"start": 2.5, "end": 5.0, "text": "第二句", "color_map": {"第二句": RED}},
]
self.run_timeline(timeline)
```

---

### 配音控制方法

| 方法 | 说明 |
|------|------|
| `set_voice(voice)` | 设置 TTS 语音，如 `"zh-CN-YunxiNeural"` |
| `set_voice_enabled(enabled)` | 启用/禁用配音生成 |
| `clear_voice_cache()` | 清理配音缓存，强制重新生成 |

---

## 字幕管理 API

### `make_subtitle(text, color_map=None) -> VGroup`

创建字幕对象（不自动显示）

```python
subtitle = self.make_subtitle("这是字幕", color_map={"字幕": YELLOW})
# subtitle[0] = 背景圆角矩形
# subtitle[1] = 文字
self.play(Write(subtitle))
```

---

### `subtitle(t0, t1, text, color_map=None)`

在指定时间段显示字幕

```python
self.subtitle(0.0, 2.5, "第一句话")
self.subtitle(2.5, 5.0, "第二句话")
```

---

### `clear_subtitle(t=None)`

清除当前字幕

```python
self.clear_subtitle()  # 立即清除
self.clear_subtitle(t=5.0)  # 在 5 秒时清除
```

---

### `set_subtitle_style(font_size=None, edge_buff=None, max_chars=None)`

自定义字幕样式

```python
self.set_subtitle_style(
    font_size=32,      # 更大字号
    edge_buff=0.3,     # 距离底部更近
    max_chars=25       # 每行更多字符
)
```

---

## 视觉引导 API

### `focus_guide(targets, ...) -> list`

**方框引导高亮** - 依次高亮多个目标

```python
formula = Tex("E = mc^2")
self.add(formula)

# 方式1: 直接指定对象
self.focus_guide([formula["E"], formula["mc^2"]])

# 方式2: 关键词查找
text = Text("向量加法满足交换律")
self.focus_guide([
    (text, "向量"),
    (text, "加法"),
    (text, "交换律")
], hold_time=1.0)
```

**参数：**
- `targets`: 目标列表
- `box_buff`: 方框边距（默认 0.1）
- `stroke_width`: 线宽（默认 3）
- `run_time`: 动画时长（默认 0.6）
- `hold_time`: 停留时间（默认 0.5）
- `auto_remove`: 结束后自动移除（默认 True）

---

### `focus_guide_sequence(text_mobject, keywords, **kwargs)`

按顺序高亮文本中的关键词（便捷方法）

```python
sentence = Text("数学中，向量加法满足交换律")
self.add(sentence)

self.focus_guide_sequence(
    sentence,
    ["向量", "加法", "交换律"],
    hold_time=1.0
)
```

---

### `focus_guide_with_camera(targets, ...) -> list`

⭐ **带相机移动的方框引导** - 更强的视觉引导效果

```python
# 相机会自动移动到每个目标并放大
self.focus_guide_with_camera(
    [formula["E"], formula["mc^2"]],
    zoom_factor=2.5,    # 放大 2.5 倍
    hold_time=1.5,      # 每个目标停留 1.5 秒
    restore_after=True  # 结束后恢复相机
)
```

**参数：**
- `zoom_factor`: 缩放倍数（默认 1.5）
- `camera_buff`: 相机边距（默认 0.5）
- `restore_after`: 结束后恢复相机（默认 True）

---

### `focus_guide_with_camera_sequence(text_mobject, keywords, **kwargs)`

带相机移动的关键词引导（便捷方法）

```python
self.focus_guide_with_camera_sequence(
    sentence,
    ["向量", "加法", "交换律"],
    zoom_factor=3.0,
    hold_time=1.5
)
```

---

### `highlight_text(target, effect="random", color=YELLOW, ...) -> Mobject`

多种高亮效果

```python
formula = Tex("E = mc^2")

# 随机效果
decoration = self.highlight_text(formula, effect="random")

# 指定效果
self.highlight_text(formula, effect="box")         # 方框
self.highlight_text(formula, effect="underline")   # 下划线
self.highlight_text(formula, effect="background")  # 背景
self.highlight_text(formula, effect="indicate")    # 缩放闪烁
self.highlight_text(formula, effect="wave")        # 波浪
self.highlight_text(formula, effect="focus")       # 聚光

# 移除高亮
self.remove_highlight(decoration)
```

---

### `add_curved_annotation(target, annotation, direction="auto", ...) -> VGroup`

弯曲箭头标注 - 将标注引到空白处避免遮挡

```python
formula = Tex("a^2 + b^2 = c^2")
self.add(formula)

# 自动选择方向
ann = self.add_curved_annotation(formula["a^2"], "直角边 a 的平方")

# 指定方向: "up", "down", "left", "right", "ur", "ul", "dr", "dl"
ann2 = self.add_curved_annotation(formula["c^2"], "斜边的平方", direction="ur")

# 移除
self.remove_curved_annotation(ann)
```

---

### `add_multi_curved_annotations(annotations, stagger=0.3, **kwargs) -> list`

批量添加弯曲箭头标注

```python
annotations = self.add_multi_curved_annotations([
    {"target": formula["a^2"], "text": "直角边a", "direction": "ul"},
    {"target": formula["b^2"], "text": "直角边b", "direction": "up"},
    {"target": formula["c^2"], "text": "斜边", "direction": "ur"},
])
```

---

### `annotate_region(region, annotation, bg_color=BLUE, ...) -> VGroup`

区域标注 - 用纯色背景覆盖区域并显示标注

```python
circle = Circle()
self.add(circle)

ann = self.annotate_region(circle, "这是一个圆", bg_color=BLUE)
self.wait(2)
self.remove_annotation(ann)
```

---

### `get_text_part(text_mobject, keyword) -> Mobject`

获取文本中关键词对应的子对象

```python
sentence = Text("向量加法满足交换律")
vec_part = self.get_text_part(sentence, "向量")
self.play(Indicate(vec_part))
```

---

### `get_text_parts(text_mobject, keywords) -> list`

获取多个关键词对应的子对象

```python
parts = self.get_text_parts(sentence, ["向量", "加法"])
for part in parts:
    self.play(Indicate(part))
```

---

## 相机控制 API

### `camera_focus(target, zoom_factor=2.0, ...)`

动态相机聚焦 - 放大到目标后恢复

```python
dot = Dot()
self.add(dot)

self.camera_focus(
    dot,
    zoom_factor=3.0,     # 放大 3 倍
    focus_time=1.0,      # 聚焦动画时长
    hold_time=2.0,       # 保持聚焦时长
    restore_time=1.0     # 恢复动画时长
)
```

---

## 固定元素 API

### `add_fixed_title(text, font_size=36, color=WHITE, ...) -> Text`

添加固定在屏幕顶部的标题

```python
title = self.add_fixed_title("第一章：向量", color=YELLOW)
self.add(title)
self.play(Write(title))
```

---

### `add_fixed_subtitle(text, color_map=None, ...) -> VGroup`

添加固定在屏幕底部的字幕

```python
sub = self.add_fixed_subtitle("这是固定字幕")
self.add(sub)
```

---

### `add_fixed_formula(tex_string, font_size=32, ...) -> Tex`

添加固定在屏幕上的公式

```python
formula = self.add_fixed_formula(r"E = mc^2", position=UP)
self.add(formula)
```

---

### `add_grid_background(...) -> VGroup`

添加低透明度网格背景

```python
grid = self.add_grid_background(step=1.0, stroke_opacity=0.1)
```

---

### `add_traffic_lights(...) -> VGroup`

添加右上角红黄绿装饰点

```python
lights = self.add_traffic_lights()
```

---

## 辉光效果 API

### `create_glow_text(text, ...) -> Group`

创建带辉光的文字

```python
title = self.create_glow_text(
    "炫酷标题",
    font_size=48,
    glow_size=0.5,
    fix_in_frame=True
)
self.add(title)
```

---

### `create_glow_tex(tex_string, ...) -> Group`

创建带辉光的 LaTeX 公式

```python
formula = self.create_glow_tex(
    r"E = mc^2",
    font_size=56,
    glow_color=BLUE
)
self.add(formula)
```

---

### `add_glow_to_curve(vmobject, ...) -> Group`

为现有曲线添加辉光

```python
circle = Circle()
glowing_circle = self.add_glow_to_curve(
    circle,
    glow_width=0.15,
    pulse=True,           # 启用脉动
    pulse_frequency=1.0
)
self.add(glowing_circle)
```

---

### `create_pulse_glow_curve(function, t_range, ...) -> GlowCurve`

创建脉动辉光参数曲线

```python
import numpy as np

curve = self.create_pulse_glow_curve(
    lambda t: np.array([t, np.sin(t), 0]),
    t_range=(-np.pi, np.pi),
    color=BLUE,
    pulse_frequency=1.5
)
self.add(curve)
```

---

### `create_pulse_glow_function(f, x_range, ...) -> GlowFunctionGraph`

创建脉动辉光函数图像

```python
curve = self.create_pulse_glow_function(
    lambda x: np.sin(x),
    x_range=(-np.pi, np.pi),
    color=BLUE
)
self.add(curve)
```

---

### `create_pulse_glow_circle(radius, ...) -> GlowCircle`

创建脉动辉光圆形

```python
circle = self.create_pulse_glow_circle(
    radius=2.0,
    color=YELLOW,
    pulse_frequency=1.0
)
self.add(circle)
```

---

## 3D 标注 API

### `add_fixed_annotation(target, label_text, direction=UP, ...) -> Text`

为 3D 对象添加始终面向相机的标注

```python
sphere = Sphere()
self.add(sphere)

label = self.add_fixed_annotation(sphere, "球体", direction=DOWN)
self.add(label)
```

---

### `add_fixed_annotation_dynamic(target, label_text, ...) -> Text`

为移动中的 3D 对象添加动态跟随的标注

```python
sphere = Sphere()
label = self.add_fixed_annotation_dynamic(sphere, "移动的球")
self.add(sphere, label)

# 标注会跟随球体移动
self.play(sphere.animate.shift(RIGHT * 3))
```

---

## 调试工具 API

### `enable_debug(enabled=True)`

启用调试模式 - 打印详细日志

```python
self.enable_debug(True)
```

---

### `enable_time_hud()`

在画面角落显示当前时间

```python
self.enable_time_hud()
```

---

### `mark(label, t=None)`

记录关键节点

```python
self.mark("开始")
# ... 一些动画 ...
self.mark("结束")

# 获取所有标记
markers = self.get_markers()
```

---

### `get_current_time() -> float`

获取当前场景时间

```python
current = self.get_current_time()
print(f"当前时间: {current:.2f}s")
```

---

### `export_srt(events, path)`

导出 SRT 字幕文件

```python
self.export_srt(timeline, "output.srt")
```

---

## 布局辅助 API

### `ensure_above_subtitle(mobject, viz_bottom_y=None, margin=0.3, overlap_buff=0.2)`

确保物体在字幕区域上方

```python
formula = Tex("E = mc^2")
self.add(formula)
self.ensure_above_subtitle(formula)
```

---

## 完整示例

### 示例 1：配音教学视频

```python
from auto_scene import AutoScene
from manimlib import Tex, Text, Write, YELLOW, RED

class TeachingDemo(AutoScene):
    def construct(self):
        self.enable_debug(True)
        
        # 标题
        title = self.add_fixed_title("向量加法", color=YELLOW)
        self.add(title)
        self.play(Write(title))
        
        # 配音讲解
        self.speak("今天我们来学习向量加法")
        
        # 创建公式
        formula = Tex(r"\vec{a} + \vec{b} = \vec{c}")
        self.play(Write(formula))
        
        # 带高亮的讲解
        self.speak_with_highlight(
            "这是向量加法的基本形式",
            targets=[formula],
            color_map={"向量加法": YELLOW}
        )
        
        # 方框引导
        self.focus_guide_with_camera(
            [formula[r"\vec{a}"], formula[r"\vec{b}"], formula[r"\vec{c}"]],
            zoom_factor=2.5,
            hold_time=1.0
        )
        
        self.speak("感谢观看！")
```

### 示例 2：公式推导

```python
class DerivationDemo(AutoScene):
    def construct(self):
        # 步骤序列
        self.speak_sequence([
            "首先，我们看问题",
            {"text": "关键是理解向量", "color_map": {"关键": YELLOW}},
            "让我们开始推导"
        ])
        
        # 公式展示
        eq1 = Tex(r"a^2 + b^2 = c^2")
        self.play(Write(eq1))
        
        # 添加标注
        annotations = self.add_multi_curved_annotations([
            {"target": eq1["a^2"], "text": "直角边a", "direction": "ul"},
            {"target": eq1["b^2"], "text": "直角边b", "direction": "up"},
            {"target": eq1["c^2"], "text": "斜边c", "direction": "ur"},
        ])
        
        self.speak("这就是勾股定理")
        
        # 清理标注
        for ann in annotations:
            self.remove_curved_annotation(ann)
```

---

## 运行方式

```bash
cd E:\auto_manim\new_class
manimgl your_script.py YourSceneClass -w
```

- 不加 `-w` 会打开预览窗口
- 加 `-w` 直接输出视频文件

---

## 注意事项

1. **字体要求**：需要安装 `STKaiti` 字体，或修改 `SUBTITLE_FONT`
2. **TTS 依赖**：配音需要 `edge-tts` 库（自动安装）
3. **辉光效果**：需要 shaderscene 模块支持
4. **音效库**：可选，需要 `sound_library.py` 模块

---

*文档生成时间: 2024-12*
