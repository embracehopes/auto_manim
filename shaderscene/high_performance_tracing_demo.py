"""
高性能 TracingTail PMobject 测试
演示使用 GPU shader 并行渲染的轨迹追踪效果
"""

import taichi as ti
import numpy as np
from manimlib import *
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
# 导入我们的高性能 TracingTail
from shadersence.mobject.TracingTailPMobject import *

# --- Taichi 设置 ---
ti.init(arch=ti.gpu)  # 使用GPU加速

# 参数设置
n_curves = 270    # 减少曲线数量以便观察效果
n_dots = 3      # 每条曲线的点数
total_points = n_curves * n_dots

# Taichi字段定义
positions = ti.Vector.field(3, dtype=float, shape=total_points)
colors_field = ti.Vector.field(3, dtype=float, shape=total_points)

# 为TracingTail预计算的参数字段
tail_parameters = ti.field(dtype=float, shape=(total_points, 8))  # 存储8个轨迹参数
# 参数顺序: [max_tail_length, tail_lifetime, opacity_start, opacity_end, width_start, width_end, glow_factor, sample_rate]

# 电影级别色彩增强字段
cinematic_colors = ti.Vector.field(3, dtype=float, shape=total_points)  # RGB增强后的颜色
color_metadata = ti.field(dtype=float, shape=(total_points, 4))  # [hue, saturation, brightness, warmth_factor]

# 物理参数
R = 3.0  # 主半径
r = 2.0  # 次半径
k1, k2, k3 = 2.0, 2.0, 2.0  # 频率参数

@ti.kernel
def compute_cardioid_torus_positions(time: float):
    """使用Taichi计算所有点的位置"""
    for i in range(total_points):
        curve_idx = i // n_dots
        dot_idx = i % n_dots
        
        # 计算每条曲线的时间偏移
        dt = 2.0 * ti.math.pi * curve_idx / n_curves
        
        # 计算点在曲线上的参数
        phase_offset = (curve_idx % 4) / 4.0
        start_positions = ti.Vector([0.0, 4.0, 8.0, 12.0])
        start_t = (start_positions[dot_idx] + phase_offset * 4.0) / 16.0
        
        # 动态时间参数
        t = start_t * 4.0 * ti.math.pi - 2.0 * ti.math.pi + time * 0.8
        
        # 心脏环面参数方程
        u = 0.8 * t
        v = t
        
        # 计算3D坐标
        x = (R + r * (2.0 * ti.cos(v/2.0) - ti.cos(k1*v))) * ti.cos(3.0*u + dt)
        y = 1.4 * r * (2.0 * ti.sin(v/2.0) - ti.sin(k2*v))
        z = (R + r * (2.0 * ti.cos(v/2.0) - ti.cos(k3*v))) * ti.sin(3.0*u + dt)

        positions[i] = ti.Vector([x, y, z])

@ti.kernel
def compute_cinematic_colors():
    """计算每个点的颜色 - 参考cardioid_torus.py的简单彩虹渐变方法"""
    for i in range(total_points):
        curve_idx = i // n_dots
        dot_idx = i % n_dots

        # === 简化的彩虹色渐变 - 参考cardioid_torus.py ===

        # 将点索引映射到色相值 (0-360度)
        hue = (i / total_points) * 360.0

        # 初始化RGB变量
        rgb = ti.Vector([1.0, 1.0, 1.0])  # 默认白色

        # 将色相转换为RGB - 实现彩虹色渐变
        if hue < 60.0:
            # RED to YELLOW
            t = hue / 60.0
            rgb = ti.Vector([1.0, t, 0.0])
        elif hue < 120.0:
            # YELLOW to GREEN
            t = (hue - 60.0) / 60.0
            rgb = ti.Vector([1.0 - t, 1.0, 0.0])
        elif hue < 180.0:
            # GREEN to TEAL
            t = (hue - 120.0) / 60.0
            rgb = ti.Vector([0.0, 1.0, t])
        elif hue < 240.0:
            # TEAL to BLUE
            t = (hue - 180.0) / 60.0
            rgb = ti.Vector([0.0, 1.0 - t, 1.0])
        elif hue < 300.0:
            # BLUE to PURPLE
            t = (hue - 240.0) / 60.0
            rgb = ti.Vector([t, 0.0, 1.0])
        else:
            # PURPLE to RED
            t = (hue - 300.0) / 60.0
            rgb = ti.Vector([1.0, 0.0, 1.0 - t])

        # 轻微的亮度调整，避免过暗或过亮
        brightness_factor = 1  # 稍微降低亮度，避免过曝
        rgb = rgb * brightness_factor

        # 确保RGB值在合理范围内
        rgb = ti.max(ti.Vector([0.0, 0.0, 0.0]), ti.min(ti.Vector([1.0, 1.0, 1.0]), rgb))

        # 存储最终颜色和元数据
        colors_field[i] = rgb
        cinematic_colors[i] = rgb
        color_metadata[i, 0] = hue
        color_metadata[i, 1] = 1.0  # 饱和度
        color_metadata[i, 2] = brightness_factor  # 亮度
        color_metadata[i, 3] = 0.0  # 暖度因子

        # === 简化的轨迹参数 - 基于简单颜色计算 ===

        # 根据粒子特性动态调整轨迹参数
        # 1. 轨迹长度 - 固定长度，避免复杂计算
        tail_length = 120.0

        # 2. 轨迹生命周期 - 固定生命周期
        tail_lifetime = 2.0

        # 3. 透明度渐变 - 简单渐变
        opacity_start = 0.7
        opacity_end = 0.0

        # 4. 宽度渐变 - 简单渐变
        width_start = 0.04
        width_end = 0.01

        # 5. 辉光强度 - 适度辉光
        glow_factor = 1.5

        # 6. 采样率 - 固定采样率
        sample_rate = 0.01

        # 存储所有轨迹参数
        tail_parameters[i, 0] = tail_length
        tail_parameters[i, 1] = tail_lifetime
        tail_parameters[i, 2] = opacity_start
        tail_parameters[i, 3] = opacity_end
        tail_parameters[i, 4] = width_start
        tail_parameters[i, 5] = width_end
        tail_parameters[i, 6] = glow_factor
        tail_parameters[i, 7] = sample_rate

# 初始化
compute_cinematic_colors()

class HighPerformanceTracingTailDemo(ThreeDScene):
    def construct(self):
        # 性能计时
        start_time = time.time()
        print("开始高性能轨迹追踪演示...")

        # 设置3D场景
        self.camera.frame.set_euler_angles(
            theta=0 * DEGREES,
            phi=0 * DEGREES
        )
        self.camera.frame.set_height(20)
        
        # 初始化Taichi计算
        compute_cardioid_torus_positions(0.0)
        compute_cinematic_colors()
        
        # 获取初始数据
        initial_positions = positions.to_numpy()
        initial_colors = colors_field.to_numpy()
        
        # 创建DotCloud显示粒子
        self.dot_cloud = DotCloud(
            points=initial_positions,
            radius=0.025,
            color=WHITE
        )
        
        # 设置粒子颜色
        num_points = len(initial_positions)
        self.dot_cloud.data = np.zeros(num_points, dtype=self.dot_cloud.data_dtype)
        self.dot_cloud.data['point'] = initial_positions
        self.dot_cloud.data['radius'] = np.full((num_points, 1), 0.025)
        rgba_colors = np.column_stack([initial_colors, np.ones(num_points)])
        self.dot_cloud.data['rgba'] = rgba_colors
        
        self.add(self.dot_cloud)
        
        # === 创建高性能 TracingTail 系统 ===
        
        # 使用Taichi预计算的参数，避免Python循环
        tail_params_np = tail_parameters.to_numpy()  # 获取所有预计算参数
        cinematic_colors_np = cinematic_colors.to_numpy()  # 获取电影级别颜色
        
        print(f"使用Taichi预计算了 {total_points} 个粒子的轨迹参数")
        
        # 批量创建追踪函数（仍需要Python函数，但数据已预计算）
        tracer_functions = []
        for i in range(total_points):
            def create_tracer(idx):
                def tracer():
                    current_positions = positions.to_numpy()
                    if idx < len(current_positions):
                        return current_positions[idx]
                    return ORIGIN
                return tracer
            tracer_functions.append(create_tracer(i))
        
        # 使用预计算的电影级别颜色和参数创建轨迹
        # 取平均值作为基础参数，避免过多变化
        avg_tail_length = int(np.mean(tail_params_np[:, 0]))
        avg_tail_lifetime = np.mean(tail_params_np[:, 1])
        avg_opacity_start = np.mean(tail_params_np[:, 2])
        avg_width_start = np.mean(tail_params_np[:, 4])
        avg_width_end = np.mean(tail_params_np[:, 5])
        avg_glow_factor = np.mean(tail_params_np[:, 6])
        
        print(f"平均轨迹参数: 长度={avg_tail_length}, 生命={avg_tail_lifetime:.2f}s, 辉光={avg_glow_factor:.2f}")
        
        # 创建多轨迹管理器，使用Taichi预计算的参数
        self.multi_tails = MultiTracingTails(
            traced_functions=tracer_functions,
            colors=cinematic_colors_np,             # 使用电影级别颜色
            max_tail_length=avg_tail_length,        # 使用平均轨迹长度
            tail_lifetime=avg_tail_lifetime,        # 使用平均生命周期
            opacity_fade=(avg_opacity_start, 0.0),  # 使用计算的透明度
            width_fade=(avg_width_start, avg_width_end),  # 使用计算的宽度
            glow_factor=avg_glow_factor,            # 使用平均辉光强度
        )
        
        self.add(self.multi_tails)
        
        # 时间和性能追踪
        self.current_time = 0.0
        self.frame_count = 0
        
        print(f"初始化完成，开始渲染 {total_points} 个粒子的轨迹...")
        print("=== 性能优化特性 ===")
        print("• Taichi GPU并行计算粒子位置和电影级别颜色")
        print("• 预计算轨迹参数，减少Python循环")
        print("• GPU shader并行渲染轨迹辉光效果")
        print("• 批量数据传输，最小化CPU-GPU通信")
        print("========================")
        
        # 定义超高性能更新器 - 最大化使用Taichi并行计算
        def ultra_high_performance_updater(mob, dt):
            self.current_time += dt
            self.frame_count += 1
            
            # 性能监控 - 减少频率以提高性能
            if self.frame_count % 180 == 0:  # 每3秒输出一次
                elapsed = time.time() - start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                particles_per_sec = self.frame_count * total_points / elapsed
                print(f"帧{self.frame_count}: FPS={fps:.1f}, 粒子/秒={particles_per_sec:.0f}K")
            
            # === 全Taichi并行计算管道 ===
            
            # 1. Taichi并行计算所有粒子的新位置和颜色
            compute_cardioid_torus_positions(self.current_time)
            
            # 2. 可选：根据运动重新计算动态颜色（电影级别实时调色）
            if self.frame_count % 30 == 0:  # 每0.5秒重新计算一次颜色，减少开销
                compute_cinematic_colors()
            
            # 3. 批量更新粒子系统（单次numpy操作，避免循环）
            new_positions = positions.to_numpy()
            self.dot_cloud.set_points(new_positions)
            
            # 4. 更新粒子颜色（可选，根据性能需求）
            if self.frame_count % 60 == 0:  # 每1秒更新一次颜色
                updated_colors = cinematic_colors.to_numpy()
                rgba_colors = np.column_stack([updated_colors, np.ones(total_points)])
                self.dot_cloud.data['rgba'] = rgba_colors
            
            # 5. GPU shader并行更新所有轨迹（已经是最优化的）
            self.multi_tails.update_all_tails(dt)
        
        # 添加超高性能更新器
        self.dot_cloud.add_updater(ultra_high_performance_updater)
        
        # 演示相机动画
        self.demo_camera_sequence()
        
        # 清理
        self.dot_cloud.clear_updaters()
        
        # 性能报告
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\\n=== 性能报告 ===")
        print(f"总时间: {total_time:.2f}秒")
        print(f"总帧数: {self.frame_count}")
        print(f"平均FPS: {self.frame_count/total_time:.2f}")
        print(f"粒子数: {total_points}")
        print(f"每秒处理粒子数: {self.frame_count * total_points / total_time:.0f}")

    def demo_camera_sequence(self):
        """演示相机动画"""
        
        # 慢速旋转观察效果
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=60 * DEGREES,
                phi=45 * DEGREES
            ).set_height(15),
            run_time=3,
            rate_func=smooth
        )
        
        # 侧面观察
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=150 * DEGREES,
                phi=30 * DEGREES
            ).set_height(12),
            run_time=3,
            rate_func=smooth
        )
        
        # 顶部观察
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=200 * DEGREES,
                phi=75 * DEGREES
            ).set_height(18),
            run_time=3,
            rate_func=smooth
        )
        
        # 回到正面
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=0 * DEGREES,
                phi=0 * DEGREES
            ).set_height(25),
            run_time=2,
            rate_func=smooth
        )


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")
