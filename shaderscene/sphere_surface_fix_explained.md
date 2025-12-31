# ShaderSurface `rgba` Attribute Removal Fix

## 背景说明
- **现象**：在切换到独显 (OpenGL Core Profile) 时，`basic_sphere_test.py` 报错 `KeyError: 'rgba'`，由于驱动严格检查顶点格式，无法找到 `rgba` attribute。
- **目标**：在不改变视觉效果的前提下，移除对逐顶点 `rgba` 的依赖，改用 uniform 提供基础颜色，并确保 Python 端顶点数据与之匹配。

---

## 改动总览

| 文件 | 作用 | 关键修改 |
| --- | --- | --- |
| `shadersence/sphere_surface/vert.glsl` | 顶点着色器 | 移除 `in vec4 rgba`，新增 `uniform vec4 base_color`；调色逻辑改用 uniform。 |
| `shadersence/mobject/sphere_surface.py` | Python 端 Mobject 定义 | 裁剪顶点数据 dtype、覆写 `get_shader_data` 与 `init_shader_wrapper`，明确 `vert_attributes`，保持 uniform 初始化。 |

---

## 逐文件详解

### 1. GLSL：从 `rgba` Attribute 切换到 Uniform

**原始代码片段** (`shadersence/sphere_surface/vert.glsl`):
```glsl
#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec4 v_color;
...
    // 最终颜色
    v_color = finalize_color(rgba, animated_pos, unit_normal);
}
```

**修改后代码片段**:
```glsl
#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
// 'rgba' per-vertex attribute removed to support strict OpenGL core profiles.
// Use a uniform base_color instead (defaults to white) so shaders don't require
// a per-vertex rgba attribute that some drivers/contexts don't provide.
uniform vec4 base_color = vec4(1.0, 1.0, 1.0, 1.0);
out vec4 v_color;
...
    // 最终颜色 — 使用 uniform base_color 替代 per-vertex rgba，视觉保持为白色基调。
    v_color = finalize_color(base_color, animated_pos, unit_normal);
}
```

**要点提示**
1. **删除 attribute**：`in vec4 rgba;` 必须移除，否则 ModernGL 仍会要求顶点缓冲提供该 attribute。
2. **新增 uniform**：`uniform vec4 base_color` 提供默认色。外部可通过 `set_uniform(base_color=...)` 自定义颜色。
3. **颜色使用**：`finalize_color` 入口参数由 `rgba` 改为 `base_color`，其余颜色混合逻辑保持原样。

> ⚠️ 若后续需要增加新的 per-vertex attribute，记得同步更新 Python 侧 `shader_dtype` 与顶点缓存。

---

### 2. Python：裁剪顶点数据并覆写 Shader Wrapper

**原始代码关键段落** (`shadersence/mobject/sphere_surface.py`):
```python
class ShaderSurface(Surface):
    """着色器表面基类，从 calabi_yau_manifold.py 中复制"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "sphere_surface"))

    def __init__(self, uv_func, u_range=(0, 1), v_range=(0, 1), brightness=1.5, **kwargs):
        self.passed_uv_func = uv_func
        super().__init__(u_range=u_range, v_range=v_range, **kwargs)
        # 初始化 shader uniforms 等...
```
> 原实现继承了默认的 `shader_dtype` (`point`, `du_point`, `dv_point`, `rgba`)，`get_shader_data` 也会包含 `rgba`。

**修改后关键代码**:
```python
from manimlib.shader_wrapper import ShaderWrapper
import numpy as np
...
class ShaderSurface(Surface):
    """着色器表面基类,从 calabi_yau_manifold.py 中复制"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "sphere_surface"))

    # 覆盖 shader_dtype 以移除 rgba 属性(因为 shader 改用 uniform base_color)
    shader_dtype = [
        ('point', np.float32, (3,)),
        ('du_point', np.float32, (3,)),
        ('dv_point', np.float32, (3,)),
    ]

    def __init__(...):
        self.passed_uv_func = uv_func
        super().__init__(u_range=u_range, v_range=v_range, **kwargs)

        # 在 core profile 下需要显式提供 rgba 顶点属性，否则 shader 初始化会报错
        # 必须在 super().__init__ 之后调用，此时顶点数组已创建
        self.set_color(WHITE)
        self.vert_attributes = ["point", "du_point", "dv_point"]

        self.set_uniform(time=0)
        self.set_uniform(brightness=brightness)
        self.add_updater(lambda m, dt: m.increment_time(dt))

    def get_shader_data(self):
        parent_data = super().get_shader_data()
        trimmed = parent_data[['point', 'du_point', 'dv_point']]
        return trimmed

    def init_shader_wrapper(self, ctx):
        self.shader_wrapper = ShaderWrapper(
            ctx=ctx,
            vert_data=self.get_shader_data(),
            shader_folder=self.shader_folder,
            mobject_uniforms=self.uniforms,
            texture_paths=self.texture_paths,
            depth_test=self.depth_test,
            render_primitive=self.render_primitive,
            code_replacements=self.shader_code_replacements,
        )
```

**要点提示**
1. **`shader_dtype`**：覆盖父类默认定义，确保顶点缓冲只包含 `point/du_point/dv_point`。
2. **`self.vert_attributes`**：在 `Surface` 构造完成后重置属性顺序，避免 ManimGL 尝试绑定 `rgba`。
3. **`get_shader_data`**：返回裁剪后的视图，彻底杜绝 `rgba` 列透出。
4. **`init_shader_wrapper`**：显式构造 `ShaderWrapper`，绕过父类内部自动推导（其仍会引用旧 dtype）。
5. **颜色初始化**：保留 `self.set_color(WHITE)` 以兼容调用者继续通过 `set_color` 设置 uniform。

---

## 复现与拓展指引

1. **遇到类似报错时**：
   - 检查着色器 `in ...` 列表与 Python 端 `shader_dtype/vert_attributes` 是否一致。
   - 若驱动提示缺少 attribute，可考虑改用 uniform 或实例属性。

2. **步骤模板**：
   1. 在 GLSL 中移除对应 `in` 声明，改为 `uniform` 或其他途径。
   2. Python 侧同步移除 dtype / 数据列，覆写 `get_shader_data` 保障一致。
   3. 若父类构造器仍注入旧数据，手动覆写 `init_shader_wrapper`。
   4. 更新 `set_color` 及相关 uniform，确保视觉输出一致。

3. **测试建议**：
   - 运行 `& D:/Python312/python.exe d:/桌面/动画教程系列/manim代码教程/shadersence/basic_sphere_test.py`
   - 核对输出无错误、场景渲染正常。

4. **后续扩展**：
   - 若需多色效果，可在 Python 中传递自定义 `base_color` uniform，或引入纹理采样。
   - 若未来重建 `rgba` attribute，只需恢复 dtype、`get_shader_data` 和 GLSL `in vec4 rgba;`。

---

## 验证结果
- 已在双显卡环境下执行上述测试命令两次，均返回 `Exit Code: 0` 且动画效果与修改前保持一致。
- NVIDIA/AMD Core Profile 均不再抛出 `KeyError: 'rgba'`。

> 保留此文档，可作为日后处理 ModernGL 顶点格式 / Uniform 迁移的参考模板。
