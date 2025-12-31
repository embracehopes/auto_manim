"""
高性能 TracingTail PMobject 测试 - 优化版
演示使用 GPU shader 并行渲染的轨迹追踪效果
优化：
1. 简化为七色线性渐变，移除复杂的颜色后处理
2. 移除不必要的Taichi字段和Python循环
3. 减少数据传输频率
4. 提供COLOR_PALETTE参数接口供调试
"""

import taichi as ti
import numpy as np
from manimlib import *
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from mobject.TracingTailPMobject import *

# --- Taichi 设置 ---
ti.init(arch=ti.gpu)

# ========== 参数设置 ==========
n_curves = 180    
n_dots = 5     
total_points = n_curves * n_dots

# ========== 七色渐变调色板（可自定义调试）==========
# 格式：7个颜色的RGB值，每个分量范围0-1
COLOR_PALETTE = np.array([
    [1.0, 0.0, 0.0],    # 红
    [1.0, 0.5, 0.0],    # 橙
    [1.0, 1.0, 0.0],    # 黄
    [0.0, 1.0, 0.0],    # 绿
    [0.0, 1.0, 1.0],    # 青
    [0.0, 0.0, 1.0],    # 蓝
    [0.5, 0.0, 1.0],    # 紫
], dtype=np.float32)

# Taichi字段定义
positions = ti.Vector.field(3, dtype=float, shape=total_points)
colors_field = ti.Vector.field(3, dtype=float, shape=total_points)

# 物理参数
R = 3.0
r = 2.0
k1, k2, k3 = 2.0, 2.0, 2.0

@ti.kernel
def compute_cardioid_torus_positions(time: float):
    """使用Taichi计算所有点的位置"""
    for i in range(total_points):
        curve_idx = i // n_dots
        dot_idx = i % n_dots
        
        dt = 2.0 * ti.math.pi * curve_idx / n_curves
        phase_offset = (curve_idx % 4) / 4.0
        start_positions = ti.Vector([0.0, 4.0, 8.0, 12.0])
        start_t = (start_positions[dot_idx] + phase_offset * 4.0) / 16.0
        t = start_t * 4.0 * ti.math.pi - 2.0 * ti.math.pi + time * 0.8
        
        u = 0.25 * t
        v = t
        
        x = (R + r * (2.0 * ti.cos(v/2.0) - ti.cos(k1*v))) * ti.cos(3.0*u + dt)
        y = 1.4 * r * (2.0 * ti.sin(v/2.0) - ti.sin(k2*v))
        z = (R + r * (2.0 * ti.cos(v/2.0) - ti.cos(k3*v))) * ti.sin(3.0*u + dt)
        
        positions[i] = ti.Vector([x, y, z])

@ti.kernel
def compute_simple_gradient_colors(palette: ti.types.ndarray()):
    """使用简化的七色线性渐变（Taichi并行计算）"""
    num_colors = 7
    
    for i in range(total_points):
        progress = float(i) / float(total_points)
        segment_float = progress * float(num_colors - 1)
        segment_idx = int(segment_float)
        
        if segment_idx >= num_colors - 1:
            segment_idx = num_colors - 2
        
        local_t = segment_float - float(segment_idx)
        
        c1_r = palette[segment_idx, 0]
        c1_g = palette[segment_idx, 1]
        c1_b = palette[segment_idx, 2]
        
        c2_r = palette[segment_idx + 1, 0]
        c2_g = palette[segment_idx + 1, 1]
        c2_b = palette[segment_idx + 1, 2]
        
        final_r = c1_r + (c2_r - c1_r) * local_t
        final_g = c1_g + (c2_g - c1_g) * local_t
        final_b = c1_b + (c2_b - c1_b) * local_t
        
        colors_field[i] = ti.Vector([final_r, final_g, final_b])

# 初始化颜色（只需调用一次）
print(f"正在初始化七色渐变... ({total_points} 个粒子)")
compute_simple_gradient_colors(COLOR_PALETTE)
print("颜色初始化完成")

class HighPerformanceTracingTailDemo(ThreeDScene):
    def construct(self):
        start_time = time.time()
        print("开始高性能轨迹追踪演示（优化版）...")

        self.camera.frame.set_euler_angles(theta=0 * DEGREES, phi=0 * DEGREES)
        self.camera.frame.set_height(20)
        
        # 初始化Taichi计算
        compute_cardioid_torus_positions(0.0)
        
        # 获取初始数据
        initial_positions = positions.to_numpy()
        initial_colors = colors_field.to_numpy()
        
        # 创建DotCloud
        self.dot_cloud = DotCloud(points=initial_positions, radius=0.025, color=WHITE)
        num_points = len(initial_positions)
        self.dot_cloud.data = np.zeros(num_points, dtype=self.dot_cloud.data_dtype)
        self.dot_cloud.data['point'] = initial_positions
        self.dot_cloud.data['radius'] = np.full((num_points, 1), 0.025)
        rgba_colors = np.column_stack([initial_colors, np.ones(num_points)])
        self.dot_cloud.data['rgba'] = rgba_colors
        
        self.add(self.dot_cloud)
        
        # 创建追踪函数
        tracer_functions = []
        for i in range(total_points):
            def create_tracer(idx):
                def tracer():
                    current_positions = positions.to_numpy()
                    return current_positions[idx] if idx < len(current_positions) else ORIGIN
                return tracer
            tracer_functions.append(create_tracer(i))
        
        # 创建多轨迹管理器（使用固定参数）
        self.multi_tails = MultiTracingTails(
            traced_functions=tracer_functions,
            colors=initial_colors,
            max_tail_length=100,
            tail_lifetime=1.8,
            opacity_fade=(1.0, 0.0),
            width_fade=(0.035, 0.008),
            glow_factor=1.0,
        )
        
        self.add(self.multi_tails)
        
        self.current_time = 0.0
        self.frame_count = 0
        
        print("=== 优化特性 ===")
        print("• 七色线性渐变（无复杂后处理）")
        print("• 移除冗余Taichi字段")
        print("• 减少CPU-GPU数据传输")
        print("• 固定轨迹参数（无动态计算）")
        print("==================")
        
        # 超高性能更新器
        def ultra_high_performance_updater(mob, dt):
            self.current_time += dt
            self.frame_count += 1
            
            # 性能监控
            if self.frame_count % 180 == 0:
                elapsed = time.time() - start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                particles_per_sec = self.frame_count * total_points / elapsed
                print(f"帧{self.frame_count}: FPS={fps:.1f}, 粒子/秒={particles_per_sec/1000:.0f}K")
            
            # 1. Taichi并行计算所有粒子的新位置
            compute_cardioid_torus_positions(self.current_time)
            
            # 2. 批量更新粒子系统
            new_positions = positions.to_numpy()
            self.dot_cloud.set_points(new_positions)
            
            # 3. GPU shader并行更新所有轨迹
            self.multi_tails.update_all_tails(dt)
        
        self.dot_cloud.add_updater(ultra_high_performance_updater)
        
        # 电影级别运镜
        self.setup_camera_movement()
        
        # 性能报告
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\n=== 性能报告 ===")
        print(f"总时间: {total_time:.2f}秒")
        print(f"总帧数: {self.frame_count}")
        print(f"平均FPS: {self.frame_count/total_time:.2f}")
        print(f"粒子数: {total_points}")
        print(f"每秒处理粒子数: {self.frame_count * total_points / total_time / 1000:.0f}K")

    def setup_camera_movement(self):
        """电影级别的运镜设置"""
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=45 * DEGREES,
                phi=60 * DEGREES
            ).set_height(16),
            run_time=5,
            rate_func=lambda t: smooth(smooth(t))
        )


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py ")
