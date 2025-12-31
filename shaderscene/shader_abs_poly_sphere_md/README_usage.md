# 球面多面体位置无关性修复 - 使用说明

## 文件概述

本修复方案包含以下文件：

1. **`shader_position_fix_documentation.md`** - 详细的问题分析和修复方案文档
2. **`fixed_spherical_polyhedra.py`** - 修复后的球面多面体类实现
3. **`position_independence_test.py`** - 完整的测试场景集合
4. **`simple_demo.py`** - 简单的演示场景
5. **`README_usage.md`** - 本使用说明文档

## 快速开始

### 1. 基本使用

```python
from fixed_spherical_polyhedra import FixedSphericalPolyhedraSphere

# 创建一个修复后的球面多面体
sphere = FixedSphericalPolyhedraSphere(
    radius=1.5,
    brightness=25,
    resolution=(60, 60)
)

# 移动球体 - shader 效果将保持一致
sphere.move_to(UP * 2)
sphere.shift(RIGHT * 3)
```

### 2. 运行演示

在终端中执行以下命令来运行演示：

```bash
# 进入项目目录
cd d:\桌面\动画教程系列\manim代码教程

# 运行简单演示
manimgl simple_demo.py SimplePositionTest

# 或运行快速演示
manimgl simple_demo.py QuickDemo
```

### 3. 运行完整测试

```bash
# 基本位置无关性测试
manimgl position_independence_test.py PositionIndependenceTest

# 多实例测试
manimgl position_independence_test.py MultipleInstanceTest

# 动画稳定性测试
manimgl position_independence_test.py AnimationStabilityTest

# 静态多面体展示
manimgl position_independence_test.py StaticPolyhedraShowcase
```

## 类和函数说明

### 主要类

#### `FixedSphericalPolyhedraSphere`
修复后的主要球面多面体类，解决了位置依赖问题。

**参数：**
- `radius` (float): 球体半径，默认 1.0
- `center` (array-like): 球体中心位置，默认 [0, 0, 0]
- `brightness` (float): 亮度系数，默认 1.5
- `time_scale` (float): 动画时间缩放，默认 1.0
- `resolution` (tuple): 球面分辨率，默认 (64, 64)

**方法：**
- `move_to(point)`: 移动到指定位置
- `shift(vector)`: 按向量位移
- `set_polyhedron_type(type_id)`: 设置多面体类型 (0-3)
- `set_animation_speed(speed)`: 设置动画速度

#### `FixedStaticPolyhedraSphere`
静态多面体球体，显示特定类型的多面体。

**参数：**
- `polyhedron_type` (str): 多面体类型，可选 "dodecahedron", "icosahedron", "cube", "octahedron"
- 其他参数同 `FixedSphericalPolyhedraSphere`

#### `FixedAnimatedPolyhedraSphere`
带自动旋转的动画球面多面体。

**附加参数：**
- `auto_rotate` (bool): 是否启用自动旋转，默认 True

**附加方法：**
- `start_auto_rotation()`: 开始自动旋转
- `stop_auto_rotation()`: 停止自动旋转

### 便捷函数

```python
# 创建特定类型的静态多面体
create_fixed_dodecahedron_sphere(radius=1.0, **kwargs)
create_fixed_icosahedron_sphere(radius=1.0, **kwargs)
create_fixed_cube_sphere(radius=1.0, **kwargs)
create_fixed_octahedron_sphere(radius=1.0, **kwargs)

# 创建动画多面体
create_fixed_animated_polyhedra_sphere(radius=1.0, **kwargs)
```

## 使用示例

### 示例 1: 基本位置无关性验证

```python
from manimlib import *
from fixed_spherical_polyhedra import FixedSphericalPolyhedraSphere

class BasicTest(Scene):
    def construct(self):
        # 创建两个相同的球体
        sphere1 = FixedSphericalPolyhedraSphere(radius=1.0, brightness=20)
        sphere2 = FixedSphericalPolyhedraSphere(radius=1.0, brightness=20)
        
        sphere1.move_to(LEFT * 2)
        sphere2.move_to(RIGHT * 2)
        
        self.add(sphere1, sphere2)
        self.wait(2)
        
        # 移动球体 - 效果应该保持一致
        self.play(
            sphere1.animate.move_to(UP * 2),
            sphere2.animate.move_to(DOWN * 2),
            run_time=3
        )
        self.wait(5)
```

### 示例 2: 不同类型的静态多面体

```python
from manimlib import *
from fixed_spherical_polyhedra import FixedStaticPolyhedraSphere

class StaticDemo(Scene):
    def construct(self):
        # 创建四种不同的多面体
        dodeca = FixedStaticPolyhedraSphere("dodecahedron", radius=1.0)
        icosa = FixedStaticPolyhedraSphere("icosahedron", radius=1.0)
        cube = FixedStaticPolyhedraSphere("cube", radius=1.0)
        octa = FixedStaticPolyhedraSphere("octahedron", radius=1.0)
        
        # 排列它们
        dodeca.move_to(UP + LEFT)
        icosa.move_to(UP + RIGHT)
        cube.move_to(DOWN + LEFT)
        octa.move_to(DOWN + RIGHT)
        
        self.add(dodeca, icosa, cube, octa)
        self.wait(10)
```

### 示例 3: 动画球体

```python
from manimlib import *
from fixed_spherical_polyhedra import FixedAnimatedPolyhedraSphere

class AnimatedDemo(Scene):
    def construct(self):
        # 创建自动旋转的球体
        sphere = FixedAnimatedPolyhedraSphere(
            radius=1.5,
            brightness=25,
            auto_rotate=True
        )
        
        self.add(sphere)
        self.wait(5)
        
        # 移动过程中旋转效果保持
        self.play(sphere.animate.move_to(UP * 2), run_time=3)
        self.wait(5)
```

## 核心修复原理

### 问题根源
原始代码在顶点着色器中使用：
```glsl
v_position = normalize(point);  // point 是世界坐标
```

### 修复方案
修复后的代码使用：
```glsl
vec3 local_position = point - sphere_center;  // 转换为本地坐标
v_position = normalize(local_position);       // 使用本地坐标
```

### 关键改进
1. **添加 `sphere_center` uniform**: 存储球体中心位置
2. **本地坐标计算**: 所有 shader 计算基于相对位置
3. **自动更新机制**: 移动时自动更新中心位置

## 性能说明

- **额外开销**: 每个顶点一次向量减法（可忽略）
- **内存开销**: 增加一个 vec3 uniform（12字节）
- **兼容性**: 完全向后兼容，API 保持不变

## 故障排除

### 常见问题

1. **导入错误**: 确保文件在正确的目录中
2. **路径问题**: 检查 `sys.path.insert` 是否指向正确的父目录
3. **Shader 编译错误**: 确认 OpenGL 版本支持（需要 3.3+）

### 调试技巧

1. 检查 uniform 更新：
```python
print(sphere.uniforms["sphere_center"])  # 应该显示当前中心位置
```

2. 验证位置计算：
```python
print(sphere.get_center())  # 球体的实际中心位置
```

3. 性能监控：
```python
# 在大量球体场景中监控帧率
import time
start_time = time.time()
# ... 渲染代码 ...
print(f"渲染时间: {time.time() - start_time:.2f}秒")
```

## 扩展和自定义

### 添加新的多面体类型

1. 在片段着色器中添加新的距离函数
2. 修改 `sel` 计算逻辑以包含新类型
3. 更新 `set_polyhedron_type` 方法

### 自定义 Shader 效果

继承 `FixedSphericalPolyhedraSphere` 并重写 shader 方法：

```python
class CustomPolyhedra(FixedSphericalPolyhedraSphere):
    def get_fixed_fragment_shader(self):
        # 返回自定义的片段着色器代码
        return """
        // 您的自定义 shader 代码
        """
```

## 总结

这个修复方案成功解决了球面多面体 shader 效果随位置变化的问题，通过：

✅ **完全解决位置依赖问题**  
✅ **保持 API 兼容性**  
✅ **优秀的性能表现**  
✅ **易于扩展和自定义**  

现在您可以自由移动球面多面体而不用担心 shader 效果的改变！
