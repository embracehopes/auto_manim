from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path

class ShaderSurface(Surface):
    """着色器表面基类，从 calabi_yau_manifold.py 中复制"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "sphere_surface"))

    def __init__(
            self,
            uv_func: Callable[[float, float], Iterable[float]],
            u_range: tuple[float, float] = (0, 1),
            v_range: tuple[float, float] = (0, 1),
            brightness = 1.5,
            **kwargs
    ):
        self.passed_uv_func = uv_func
        super().__init__(u_range=u_range, v_range=v_range, **kwargs)

        # 初始化shader uniforms
        self.set_uniform(time=0)
        self.set_uniform(brightness=brightness)

        # 添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))

    def uv_func(self, u, v):
        return self.passed_uv_func(u, v)

    def increment_time(self, dt):
        self.uniforms["time"] += 1 * dt
        return self


class SphereSurface(ShaderSurface):
    """使用 ShaderSurface 实现的球体表面"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (510, 510),
        brightness: float = 1.5,
        **kwargs
    ):
        self.radius = radius
        self.center = np.array(center)
        
        def sphere_func(u, v):
            # 球面参数方程
            # u: 经度 (0 到 2π)
            # v: 纬度 (0 到 π)
            x = self.radius * sin(v) * cos(u) + self.center[0]
            y = self.radius * sin(v) * sin(u) + self.center[1]
            z = self.radius * cos(v) + self.center[2]
            return np.array([x, y, z])
        
        super().__init__(
            uv_func=sphere_func,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )


class EarthSphere(SphereSurface):
    """地球样式的球体，带有纹理映射效果"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 1.2,
        **kwargs
    ):
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        # 设置地球样式的颜色
        self.set_color(BLUE)


class AnimatedSphere(SphereSurface):
    """带有动画效果的球体"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        wave_amplitude: float = 0.1,
        wave_frequency: float = 2.0,
        brightness: float = 1.5,
        **kwargs
    ):
        self.wave_amplitude = wave_amplitude
        self.wave_frequency = wave_frequency
        
        def animated_sphere_func(u, v):
            # 基础球面
            base_radius = radius
            # 添加时间相关的波动效果
            time_factor = self.uniforms.get("time", 0)
            wave_offset = self.wave_amplitude * sin(self.wave_frequency * u + time_factor) * sin(self.wave_frequency * v)
            effective_radius = base_radius + wave_offset
            
            x = effective_radius * sin(v) * cos(u) + center[0]
            y = effective_radius * sin(v) * sin(u) + center[1]
            z = effective_radius * cos(v) + center[2]
            return np.array([x, y, z])
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        # 重新设置 uv_func 以支持动画
        self.passed_uv_func = animated_sphere_func


class PlanetSphere(SphereSurface):
    """行星样式的球体，带有自转效果"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        rotation_speed: float = 1.0,
        brightness: float = 1.3,
        color: str = BLUE,
        **kwargs
    ):
        self.rotation_speed = rotation_speed
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        self.set_color(color)
        
        # 添加自转效果
        self.add_updater(lambda m, dt: m.rotate(
            self.rotation_speed * dt, 
            axis=UP
        ))


class TexturedSphere(SphereSurface):
    """带有纹理效果的球体"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        texture_scale: float = 4.0,
        brightness: float = 1.4,
        **kwargs
    ):
        self.texture_scale = texture_scale
        
        def textured_sphere_func(u, v):
            # 基础球面
            x = radius * sin(v) * cos(u) + center[0]
            y = radius * sin(v) * sin(u) + center[1]
            z = radius * cos(v) + center[2]
            return np.array([x, y, z])
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置纹理相关的 uniform
        self.set_uniform(texture_scale=texture_scale)


class PlasmaGlobe(SphereSurface):
    """等离子球 - 使用特殊的着色器效果"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        mouse_pos: Iterable[float] = [0, 0],
        resolution_scale: float = 1.0,
        **kwargs
    ):
        self.mouse_pos = np.array(mouse_pos)
        self.resolution_scale = resolution_scale
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置等离子球特有的 uniform 变量
        self.set_uniform(mouse=self.mouse_pos)
        self.set_uniform(resolution=np.array([800 * resolution_scale, 600 * resolution_scale]))
        
        # 添加鼠标位置更新器（可以通过动画控制）
        self.add_updater(self.update_mouse_position)
    
    def update_mouse_position(self, mobject, dt=0):
        """更新鼠标位置，可以用于动画效果"""
        # 这里可以添加自动的鼠标移动效果
        t = self.uniforms.get("time", 0)
        auto_mouse_x = 400 * (1 + 0.3 * np.sin(t * 0.5)) * self.resolution_scale
        auto_mouse_y = 300 * (1 + 0.3 * np.cos(t * 0.7)) * self.resolution_scale
        self.set_uniform(mouse=np.array([auto_mouse_x, auto_mouse_y]))
        return self
    
    def set_mouse_position(self, x: float, y: float):
        """手动设置鼠标位置"""
        self.mouse_pos = np.array([x, y])
        self.set_uniform(mouse=self.mouse_pos)
        return self
    
    def set_resolution(self, width: int, height: int):
        """设置分辨率"""
        self.set_uniform(resolution=np.array([width, height]))
        return self


class WorkingPlasmaGlobe(SphereSurface):
    """工作的等离子球 - 使用内联着色器代码"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        mouse_pos: Iterable[float] = [400, 300],
        resolution_scale: float = 1.0,
        num_rays: float = 8.0,
        **kwargs
    ):
        self.mouse_pos = np.array(mouse_pos)
        self.resolution_scale = resolution_scale
        self.num_rays = num_rays
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置uniform变量
        self.set_uniform(mouse=self.mouse_pos)
        self.set_uniform(resolution=np.array([800 * resolution_scale, 600 * resolution_scale]))
        self.set_uniform(num_rays=num_rays)
        
        # 添加鼠标位置更新器
        self.add_updater(self.update_mouse_position)
    
    def get_shader_program_id(self):
        """返回工作着色器程序ID"""
        return "working_plasma_globe"
    
    def get_shader_code(self):
        """返回内联着色器代码"""
        # 直接返回着色器代码，避免文件读取
        vertex_shader = """
#version 330

in vec3 point;
in vec3 du_point;
in vec3 dv_point;

uniform mat4 view;
uniform mat4 projection;

out vec3 verts;
out vec3 v_normal;
out vec2 v_uv;
out vec4 v_color;

void main() {
    verts = point;
    v_normal = normalize(cross(du_point, dv_point));
    
    // Generate UV coordinates from sphere position
    float u = 0.5 + atan(point.z, point.x) / (2.0 * 3.14159265359);
    float v = 0.5 - asin(point.y) / 3.14159265359;
    v_uv = vec2(u, v);
    
    v_color = vec4(1.0, 1.0, 1.0, 1.0);
    
    gl_Position = projection * view * vec4(point, 1.0);
}
"""
        
        fragment_shader = """
#version 330

uniform float time;
uniform float brightness;
uniform vec2 resolution;
uniform vec2 mouse;
uniform float num_rays;

in vec3 verts;
in vec3 v_normal;
in vec2 v_uv;
in vec4 v_color;

out vec4 frag_color;

// Generate noise function
float noise(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    // Use UV coordinates from the sphere
    vec2 uv = v_uv * 2.0 - 1.0;
    
    // Center point for plasma effect
    vec2 center = vec2(0.0, 0.0);
    float dist = length(uv - center);
    float angle = atan(uv.y - center.y, uv.x - center.x);
    
    // Generate multiple plasma rays
    float plasma = 0.0;
    for (float i = 0.0; i < num_rays; i++) {
        float rayAngle = angle + i * 0.78539816339; // PI/4
        float ray = sin(rayAngle * 4.0 + time * 2.0) * 0.5 + 0.5;
        plasma += exp(-dist * 8.0) * ray;
    }
    
    // Add some noise for organic effect
    float n = noise(uv * 10.0 + time);
    plasma += n * 0.1;
    
    // Color gradient from blue to purple to orange
    vec3 color1 = vec3(0.1, 0.2, 0.8);  // Blue
    vec3 color2 = vec3(0.8, 0.2, 0.8);  // Purple  
    vec3 color3 = vec3(1.0, 0.5, 0.2);  // Orange
    
    vec3 finalColor = mix(color1, color2, plasma);
    finalColor = mix(finalColor, color3, plasma * 0.5);
    
    // Apply brightness
    finalColor *= brightness;
    
    frag_color = vec4(finalColor, 1.0);
}
"""
        
        return {"vertex_shader": vertex_shader, "fragment_shader": fragment_shader}
    
    def update_mouse_position(self, mobject, dt=0):
        """更新鼠标位置，创建动态交互效果"""
        t = self.uniforms.get("time", 0)
        # 创建动态的鼠标轨迹
        mouse_x = 400 + 150 * np.sin(t * 0.6) * np.cos(t * 0.2)
        mouse_y = 300 + 100 * np.cos(t * 0.4) * np.sin(t * 0.3)
        self.set_uniform(mouse=np.array([mouse_x, mouse_y]))
        return self
    
    def set_mouse_position(self, x: float, y: float):
        """手动设置鼠标位置"""
        self.mouse_pos = np.array([x, y])
        self.set_uniform(mouse=self.mouse_pos)
        return self
    
    def set_resolution(self, width: int, height: int):
        """设置分辨率"""
        self.set_uniform(resolution=np.array([width, height]))
        return self
    
    def set_num_rays(self, num_rays: float):
        """设置光线数量"""
        self.num_rays = num_rays
        self.set_uniform(num_rays=num_rays)
        return self


class FullPlasmaGlobe(SphereSurface):
    """完整的等离子球 - 使用完整的 Shadertoy 着色器实现"""
    
    shader_folder: str = str(Path(Path(__file__).parent.parent / "sphere_surface"))
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        mouse_pos: Iterable[float] = [400, 300],
        resolution_scale: float = 1.0,
        num_rays: float = 12.0,
        **kwargs
    ):
        # 重写 shader_folder 以使用专门的等离子球着色器
        self.shader_folder = str(Path(Path(__file__).parent.parent / "sphere_surface"))
        self.mouse_pos = np.array(mouse_pos)
        self.resolution_scale = resolution_scale
        self.num_rays = num_rays
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置等离子球特有的 uniform 变量
        self.set_uniform(mouse=self.mouse_pos)
        self.set_uniform(resolution=np.array([800 * resolution_scale, 600 * resolution_scale]))
        self.set_uniform(num_rays=num_rays)
        
        # 添加鼠标位置更新器
        self.add_updater(self.update_mouse_position)
    
    def get_shader_program_id(self):
        """返回自定义的着色器程序ID"""
        return "plasma_globe"
    
    def get_shader_code(self):
        """返回等离子球专用的着色器代码"""
        import os
        
        # 读取专门的等离子球着色器
        vert_path = os.path.join(self.shader_folder, "plasma_vert.glsl")
        frag_path = os.path.join(self.shader_folder, "plasma_frag.glsl")
        
        try:
            with open(vert_path, 'r') as f:
                vert_code = f.read()
            with open(frag_path, 'r') as f:
                frag_code = f.read()
                
            return {"vertex_shader": vert_code, "fragment_shader": frag_code}
        except FileNotFoundError:
            # 如果专门的着色器文件不存在，回退到默认
            return super().get_shader_code()
    
    def update_mouse_position(self, mobject, dt=0):
        """更新鼠标位置，创建动态交互效果"""
        t = self.uniforms.get("time", 0)
        # 创建更有趣的鼠标轨迹
        mouse_x = 400 + 200 * np.sin(t * 0.8) * np.cos(t * 0.3)
        mouse_y = 300 + 150 * np.cos(t * 0.6) * np.sin(t * 0.4)
        self.set_uniform(mouse=np.array([mouse_x, mouse_y]))
        return self
    
    def set_mouse_position(self, x: float, y: float):
        """手动设置鼠标位置"""
        self.mouse_pos = np.array([x, y])
        self.set_uniform(mouse=self.mouse_pos)
        return self
    
    def set_resolution(self, width: int, height: int):
        """设置分辨率"""
        self.set_uniform(resolution=np.array([width, height]))
        return self
    
    def set_num_rays(self, num_rays: float):
        """设置光线数量"""
        self.num_rays = num_rays
        self.set_uniform(num_rays=num_rays)
        return self


class InteractivePlasmaGlobe(PlasmaGlobe):
    """交互式等离子球 - 支持更复杂的交互效果"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.5,
        num_rays: int = 12,
        interaction_strength: float = 1.0,
        **kwargs
    ):
        self.num_rays = num_rays
        self.interaction_strength = interaction_strength
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置交互相关的 uniform
        self.set_uniform(num_rays=float(num_rays))
        self.set_uniform(interaction_strength=interaction_strength)
    
    def create_touch_effect(self, touch_points: list):
        """创建多点触摸效果"""
        if len(touch_points) > 0:
            # 使用第一个触摸点作为主要交互点
            main_touch = touch_points[0]
            self.set_mouse_position(main_touch[0], main_touch[1])
        return self


# 使用示例函数
def create_simple_sphere(axes=None):
    """创建一个简单的球体"""
    if axes is None:
        axes = ThreeDAxes()
    
    sphere = SphereSurface(
        radius=2.0,
        center=[0, 0, 0],
        brightness=1.5
    )
    sphere.set_color(BLUE)
    return sphere


def create_earth_sphere(axes=None):
    """创建一个地球样式的球体"""
    if axes is None:
        axes = ThreeDAxes()
    
    earth = EarthSphere(
        radius=2.0,
        center=[0, 0, 0],
        brightness=1.2
    )
    return earth


def create_animated_sphere(axes=None):
    """创建一个有动画效果的球体"""
    if axes is None:
        axes = ThreeDAxes()
    
    animated = AnimatedSphere(
        radius=2.0,
        center=[0, 0, 0],
        wave_amplitude=0.2,
        wave_frequency=3.0,
        brightness=1.5
    )
    animated.set_color(GREEN)
    return animated


def create_planet_sphere(axes=None, color=RED):
    """创建一个自转的行星球体"""
    if axes is None:
        axes = ThreeDAxes()
    
    planet = PlanetSphere(
        radius=2.0,
        center=[0, 0, 0],
        rotation_speed=0.5,
        brightness=1.3,
        color=color
    )
    return planet


def create_simple_plasma_globe(axes=None):
    """创建一个简化的等离子球（更稳定）"""
    if axes is None:
        axes = ThreeDAxes()
    
    plasma = WorkingPlasmaGlobe(
        radius=2.0,
        center=[0, 0, 0],
        brightness=2.0,
        resolution_scale=1.0,
        num_rays=8.0
    )
    return plasma


def create_plasma_globe(axes=None):
    """创建一个等离子球"""
    if axes is None:
        axes = ThreeDAxes()
    
    plasma = PlasmaGlobe(
        radius=2.0,
        center=[0, 0, 0],
        brightness=2.0,
        resolution_scale=1.0
    )
    return plasma


def create_interactive_plasma_globe(axes=None):
    """创建一个交互式等离子球"""
    if axes is None:
        axes = ThreeDAxes()
    
    interactive_plasma = InteractivePlasmaGlobe(
        radius=2.0,
        center=[0, 0, 0],
        brightness=2.5,
        num_rays=15,
        interaction_strength=1.2
    )
    return interactive_plasma


def create_full_plasma_globe(axes=None):
    """创建一个完整的等离子球（使用完整 Shadertoy 实现）"""
    if axes is None:
        axes = ThreeDAxes()
    
    full_plasma = FullPlasmaGlobe(
        radius=2.0,
        center=[0, 0, 0],
        brightness=2.0,
        resolution_scale=1.0,
        num_rays=12.0
    )
    return full_plasma


def create_high_quality_plasma_globe(axes=None):
    """创建一个高质量等离子球"""
    if axes is None:
        axes = ThreeDAxes()
    
    hq_plasma = FullPlasmaGlobe(
        radius=2.5,
        center=[0, 0, 0],
        brightness=2.5,
        resolution_scale=1.5,
        num_rays=25.0
    )
    return hq_plasma


class GeodesicSphere(SphereSurface):
    """测地线球体 - 使用原shader代码的geodesic tiling效果"""
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        subdivisions: float = 3.0,
        **kwargs
    ):
        self.subdivisions = subdivisions
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置uniform变量
        self.set_uniform(subdivisions=subdivisions)
        
        # 添加时间更新器
        self.add_updater(self.update_time)
    
    def get_shader_program_id(self):
        """返回geodesic着色器程序ID"""
        return "geodesic_sphere"
    
    def get_shader_code(self):
        """返回简化的geodesic球体着色器代码"""
        vertex_shader = """
#version 330

in vec3 point;
in vec3 du_point;
in vec3 dv_point;

uniform mat4 view;
uniform mat4 projection;

out vec3 verts;
out vec3 v_normal;
out vec2 v_uv;

void main() {
    verts = point;
    v_normal = normalize(cross(du_point, dv_point));
    
    // 从球面坐标生成UV
    vec3 n = normalize(point);
    v_uv = vec2(
        atan(n.z, n.x) / (2.0 * 3.14159265359) + 0.5,
        asin(n.y) / 3.14159265359 + 0.5
    );
    
    gl_Position = projection * view * vec4(point, 1.0);
}
"""
        
        fragment_shader = """
#version 330

uniform float time;
uniform float brightness;
uniform float subdivisions;

in vec3 verts;
in vec3 v_normal;
in vec2 v_uv;

out vec4 frag_color;

// 简单的颜色调色板
vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.0, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    // 归一化球面坐标
    vec3 pos = normalize(verts);
    
    // 创建六边形网格模式
    vec2 grid = v_uv * subdivisions;
    vec2 gid = floor(grid);
    vec2 guv = fract(grid);
    
    // 简单的六边形近似
    float dist = length(guv - 0.5);
    float hex = smoothstep(0.4, 0.45, dist);
    
    // 基于位置和时间的颜色
    float colorTime = length(pos.xy) + time * 0.2;
    vec3 baseColor = palette(colorTime);
    
    // 混合边缘和面的颜色
    vec3 faceColor = vec3(0.1, 0.1, 0.2);
    vec3 edgeColor = baseColor;
    
    vec3 finalColor = mix(edgeColor, faceColor, hex);
    
    // 添加一些动画效果
    float wave = sin(time * 2.0 + pos.x * 5.0) * 0.5 + 0.5;
    finalColor += baseColor * wave * 0.1;
    
    // 应用亮度
    finalColor *= brightness;
    
    frag_color = vec4(finalColor, 1.0);
}
"""
        
        return {"vertex_shader": vertex_shader, "fragment_shader": fragment_shader}
    
    def update_time(self, mobject, dt=0):
        """更新时间uniform"""
        current_time = self.uniforms.get("time", 0) + dt
        self.set_uniform(time=current_time)
        return self
    
    def set_subdivisions(self, subdivisions: float):
        """设置细分数"""
        self.subdivisions = subdivisions
        self.set_uniform(subdivisions=subdivisions)
        return self


# 便利函数
def create_geodesic_sphere(axes=None):
    """创建测地线球体"""
    if axes is None:
        axes = ThreeDAxes()
    
    geodesic = GeodesicSphere(
        radius=2.0,
        center=[0, 0, 0],
        brightness=2.0,
        subdivisions=3.0
    )
    return geodesic
