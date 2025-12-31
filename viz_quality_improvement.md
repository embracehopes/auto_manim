# 提升 AI 可视化生成品质方案

> 目标：让 AI 生成的可视化区域更具吸引力、动态感和专业品味

---

## 问题诊断

当前 AI 生成的可视化常见问题：
1. **静态呆板** - 缺乏动态元素，只有配音在变
2. **配色单调** - 使用默认颜色，缺乏视觉层次
3. **缺乏焦点** - 不知道该看哪里
4. **千篇一律** - 同类型题目可视化高度雷同

---

## 方案一：提示词工程增强

### 1.1 强制动态要求（在 AI-2 提示词中）

```markdown
可视化区必须满足以下至少 2 项：
□ ValueTracker 驱动的数值动态显示
□ 游标/高亮点沿曲线移动
□ 呼吸高亮（周期性 stroke_width/opacity）
□ 区域填充渐变动画
□ 相机微平移/缩放
□ 扫描线/进度条效果
```



### 1.3 增加"可视化意图"字段

在 JSON 时间轴中增加 `viz_intent` 字段：

```json
{
  "scene_id": "S5",
  "visual_action": "可视化",
  "viz_intent": {
    "type": "coordinate_system",  // 坐标系/数轴/区域/图形变换
    "focus": "region_fill",       // 重点：区域填充
    "dynamic": "sweep_reveal",    // 动态方式：扫描揭示
    "highlight": ["valid_region", "boundary_line"]
  }
}
```

---

## 方案二：可视化模板库

### 2.1 模板分类

```
viz_templates/
├── coordinate/           # 坐标系相关
│   ├── point_grid.py     # 整数点网格（概率计数）
│   ├── region_fill.py    # 区域填充（几何概型）
│   ├── curve_trace.py    # 曲线追踪（函数图像）
│   └── vector_field.py   # 向量场
├── geometry/             # 几何图形
│   ├── triangle_aux.py   # 三角形辅助线
│   ├── circle_tangent.py # 圆与切线
│   └── conic_section.py  # 圆锥曲线
├── algebra/              # 代数可视化
│   ├── equation_balance.py # 方程天平
│   ├── inequality_number_line.py # 不等式数轴
│   └── polynomial_roots.py # 多项式根
└── probability/          # 概率统计
    ├── sample_space.py   # 样本空间
    ├── venn_diagram.py   # 韦恩图
    └── distribution.py   # 分布图
```


## 方案三：动态效果增强

### 3.1 必备动态效果清单

| 效果类型 | 实现方式 | 适用场景 |
|----------|----------|----------|
| **数值跟踪** | `ValueTracker` + `DecimalNumber` | 参数变化展示 |
| **游标移动** | `Dot.add_updater(path.point_from_proportion)` | 曲线追踪 |
| **区域揭示** | `UpdateFromAlphaFunc` + `clip_path` | 几何概型 |
| **呼吸高亮** | `t.add_updater(np.sin(time))` | 强调关键对象 |
| **颜色渐变** | `interpolate_color(c1, c2, alpha)` | 条件变化 |
| **扫描线** | `Line.add_updater(sweep_x)` | 积分/求和 |


---

## 方案四：案例参考库

### 4.1 建立参考案例库

```
viz_references/
├── probability/
│   ├── discrete_counting.md      # 离散计数（附代码+效果图）
│   ├── geometric_probability.md  # 几何概型
│   └── conditional_probability.md
├── function/
│   ├── piecewise_function.md     # 分段函数
│   ├── odd_even_symmetry.md      # 奇偶对称
│   └── transformations.md        # 函数变换
└── geometry/
    ├── triangle_problems.md
    └── conic_sections.md
```

### 4.2 案例格式

```markdown
# 案例：整数点计数（概率问题）



## 方案五：AI 提示词改进对照表

| 原提示词 | 改进后 |
|----------|--------|
| "可视化区至少1个updater" | "可视化区必须有持续运动元素（游标/数值/呼吸高亮），每3秒内必须有可见变化" |
| "静态内容加轻量动态" | "禁止纯静态画面超过2秒， |
| "颜色策略：默认白" | "使用电影级调色板：主色#FF6B6B，辅色#4ECDC4，高亮#FFE66D" |


---
---

## 方案八：质量评估指标与交付检查

### 8.1 可量化指标

| 节奏 | 纯静止画面 <= 2s | 时间轴检查 |



### 8.3 交付前检查清单
- [ ] 主视觉锚点明显，能在 3 秒内定位
- [ ] 动态元素满足数量要求且无突兀跳变
- [ ] 色彩数量受控，强调色只用于关键对象
- [ ] 公式/单位/刻度标注齐全
- [ ] 采样点验证区域正确
- [ ] 文本无遮挡、不过密、不过边

---

## 实施建议

### 短期（立即可做）
- [ ] 在提示词中增加"动态效果必选清单"
- [ ] 增加颜色调色板约束
- [ ] 增加"每3秒必须有变化"规则
- [ ] 增加视觉锚点与版式对齐约束
- [ ] 增加准确性校验清单

### 中期（1-2周）
- [ ] 建立 `viz_templates/` 模板库（5-10个常用模板）
- [ ] 编写 `DynamicEffects` 工具类并附最小可运行示例
- [ ] 建立 3-5 个高质量参考案例
- [ ] 抽取 `viz_style_tokens.py` 统一风格参数

### 长期（持续迭代）
- [ ] 根据实际效果反馈优化模板
- [ ] 扩展案例库覆盖更多题型
- [ ] 评估自动化质量评分/校验脚本
- [ ] 考虑使用向量数据库实现"相似题目可视化推荐"

---

## 附录：推荐调色板

```python
# 电影级调色板
PALETTE = {
    "coral_red": "#FF6B6B",      # 珊瑚红（强调）
    "tiffany_blue": "#4ECDC4",   # 蒂芙尼蓝（辅助）
    "lemon_yellow": "#FFE66D",   # 柠檬黄（高亮）
    "mint_green": "#95E1D3",     # 薄荷绿
    "rose_pink": "#F38181",      # 玫瑰粉
    "lavender": "#AA96DA",       # 薰衣草紫
    "sky_blue": "#A8D8EA",       # 天空蓝
    "orange": "#FF9F43",         # 橘子橙
    "neon_green": "#54E346",     # 荧光绿
}
```

---



---

## 方案十一：3D 与相机高级运用

### 11.1 3D 场景增强
```python
# 3D 场景常用配置
self.camera.frame.set_euler_angles(
    theta=30 * DEGREES,  # 水平旋转
    phi=70 * DEGREES,    # 俯仰角
)

# 添加环境光感
self.camera.light_source.move_to(3*UP + 5*OUT + 2*RIGHT)

# 3D 对象阴影效果
surface.set_shadow(0.5)
```

### 11.2 相机运动技巧
| 运动类型 | 代码示例 | 效果 |
|----------|----------|------|
| **聚焦放大** | `self.camera.frame.animate.set_height(h*0.5).move_to(target)` | 突出局部细节 |
| **全景回退** | `self.camera.frame.animate.set_height(h*2)` | 展示全局关系 |
| **跟随对象** | `self.camera.frame.add_updater(follow_func)` | 动态追踪 |
| **环绕旋转** | `Rotate(frame, angle, axis=OUT)` | 3D 展示 |




### 12.3 标注位置规则
```markdown
标注放置原则：
- 优先放在空白区域（不遮挡主图形）
- 与目标对象距离 0.2-0.5 单位
- 使用 next_to + 微调，避免 move_to 硬编码
- 多个标注使用一致的对齐方式
```

### 12.4 数值标注动态更新
```python
# 数值随 tracker 变化
value_label = DecimalNumber(0, num_decimal_places=2)
value_label.add_updater(
    lambda m: m.set_value(tracker.get_value())
)
value_label.add_updater(
    lambda m: m.next_to(target_point, UP)
)
```

---

## 方案十三：配音同步与节奏控制

### 13.1 配音-动画同步原则
```markdown
同步规则：
1. 动画开始时机 = 配音提及该内容的时刻
2. 复杂动画先于配音 0.3-0.5s 开始（预读效果）
3. 关键结论配音后保持画面 1-2s（消化时间）
4. 避免配音空档期 > 3s 的纯静态画面
```

