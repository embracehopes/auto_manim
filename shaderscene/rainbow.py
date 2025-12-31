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
from mobject.TracingTailPMobject import *

# --- Taichi 设置 ---
ti.init(arch=ti.gpu)  # 使用GPU加速

# 参数设置
n_curves = 180    # 减少曲线数量以便观察效果
n_dots = 5      # 每条曲线的点数
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
R1 = 4.0
r = 1.0
R = 7.0
h = -1.0

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
        
        # 调整 u 和 v 到 [0, 2π] 范围
        u =  0.25*t+dt 
        v = t 
        
        # 计算3D坐标
        x = (R1 + (R - r) * ti.cos(v) + h * ti.cos(((R - r) / r) * v)) * ti.cos(u)
        y = 1.5 * (R - r) * ti.sin(v) - h * ti.sin(((R - r) / r) * v)
        z = (R1 + (R - r) * ti.cos(v) + h * ti.cos(((R - r) / r) * v)) * ti.sin(u)
        
        positions[i] = ti.Vector([x, y, z])

def _calculate_cinematic_rainbow_color(index, total_points):
    """计算柔和彩虹渐变色 - 使用指定的柔和色调"""
    import math
    
    # 模仿cardioid_torus.py的逻辑：确保整个系统只显示一轮完整的彩虹色
    # 将粒子索引线性映射到色相值 (0-100%)
    progress = index / total_points
    
    # 使用指定的柔和色彩: CDB4DB, FFC8DD, FFAFCC, BDE0FE, A2D2FF
    soft_colors = [
        "#570487",  # 柔和紫色
        "#8A0538",  # 柔和粉色
        "#0D8307",  # 柔和粉红
        "#044A88",  # 柔和蓝色
        "#A66408",  # 柔和天蓝
        "#000C8C"   # 回到起始颜色形成循环
    ]
    
    # 计算所在的颜色段
    num_segments = len(soft_colors) - 1
    segment_idx = int(progress * num_segments)
    segment_idx = min(segment_idx, num_segments - 1)  # 确保索引有效
    
    # 计算在当前段内的进度 (0-1)
    segment_progress = (progress * num_segments) - segment_idx
    
    # 在两个相邻颜色之间进行插值
    color1 = soft_colors[segment_idx]
    color2 = soft_colors[segment_idx + 1]
    
    # 使用ManimGL的颜色插值，加入轻微的中间调增强
    base_color = interpolate_color(color1, color2, segment_progress)
    
    # 特殊过渡增强 - 让颜色过渡更加平滑
    if 0.4 < segment_progress < 0.6:
        # 在中间区域增加一些微妙的混合
        mid_factor = 1.0 - abs(segment_progress - 0.5) * 5  # 0.4-0.6 映射到 0.5-0.0
        
        # 根据所在段选择适当的中间色调增强
        if segment_idx == 0:  # 紫色到粉色
            mid_color = "#DB6DF9"  # 更淡的紫粉色
        elif segment_idx == 1:  # 粉色到粉红
            mid_color = "#FD82B1"  # 中间粉红色
        elif segment_idx == 2:  # 粉红到蓝色
            mid_color = "#9668F3"  # 淡紫蓝色
        elif segment_idx == 3:  # 蓝色到天蓝
            mid_color = "#79BEF7"  # 浅蓝色
        else:  # 天蓝到紫色
            mid_color = "#786FEF"  # 淡紫蓝色
            
        # 轻微混合中间色调
        base_color = interpolate_color(base_color, mid_color, mid_factor * 0.1)
    
    return base_color

@ti.kernel
def compute_cinematic_colors():
    """计算每个点的颜色 - 柔和彩虹色彩处理"""
    for i in range(total_points):
        # 从预计算的颜色数组中获取RGB值
        rgb = ti.Vector([
            cinematic_colors[i][0],
            cinematic_colors[i][1], 
            cinematic_colors[i][2]
        ])
        
        # === 柔和色彩后处理 ===
        
        # 1. 计算当前颜色的感知亮度
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        
        # 2. 轻微降低对比度 - 让颜色更加柔和
        contrast_factor = 0.95  # 降低对比度
        contrast_center = 1  # 以中等亮度为中心
        rgb = contrast_center + (rgb - contrast_center) * contrast_factor
        
        # 3. 降低饱和度 - 创造更柔和的效果
        curve_idx = i // n_dots
        # 轻微的饱和度波动，但整体降低饱和度
        saturation_factor = 0.85 + 0.05 * ti.sin(curve_idx * 0.1)  
        
        # 计算色彩的饱和度并调整
        max_channel = ti.max(ti.max(rgb[0], rgb[1]), rgb[2])
        min_channel = ti.min(ti.min(rgb[0], rgb[1]), rgb[2])
        
        if max_channel > min_channel:
            # 调整饱和度
            center = (max_channel + min_channel) * 0.5
            rgb = center + (rgb - center) * saturation_factor
        
        # 4. 添加微妙的暖色调 - 让颜色更舒适
        depth_factor = ti.sin(curve_idx / n_curves * ti.math.pi)
        
        # 整体轻微增加暖色
        warm_boost = 0.05  # 轻微的暖色提升
        rgb[0] = ti.min(1.0, rgb[0] * (1.0 + warm_boost))  # 增强红色
        rgb[1] = ti.min(1.0, rgb[1] * (1.0 + warm_boost * 0.5))  # 轻微增强绿色
        
        # 5. 柔和伽马校正
        gamma = 1.1  # 轻微提高伽马值，增强柔和感
        rgb = ti.pow(rgb, gamma)
        
        # 6. 最终颜色限制和平衡 - 确保柔和效果
        rgb = ti.max(ti.Vector([0.05, 0.05, 0.05]), ti.min(ti.Vector([0.95, 0.95, 0.95]), rgb))
        
        # 存储最终颜色和元数据
        colors_field[i] = rgb
        
        # 更新颜色元数据
        hue = (i / total_points) * 360.0  # 线性色相分布
        saturation_factor = 0.85 + 0.05 * ti.sin(curve_idx * 0.1)  # 保存当前使用的饱和度因子
        
        color_metadata[i, 0] = hue
        color_metadata[i, 1] = saturation_factor  # 实际饱和度值
        color_metadata[i, 2] = luminance  # 感知亮度
        color_metadata[i, 3] = depth_factor  # 深度因子

        # === 简化的轨迹参数 - 基于简单颜色计算 ===

        # 根据粒子特性动态调整轨迹参数
        # 1. 轨迹长度 - 固定长度，避免复杂计算
        tail_length = 100.0
        
        # 2. 轨迹生命周期 - 固定生命周期
        tail_lifetime = 1.8
        
        # 3. 透明度渐变 - 降低整体透明度
        opacity_start = 1
        opacity_end = 0.0

        # 4. 宽度渐变 - 统一细线条
        width_start = 0.035
        width_end = 0.008
        
        # 5. 辉光强度 - 柔和辉光
        glow_factor = 1.2
        
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

# 预计算所有颜色使用电影级别彩虹插值
print("正在预计算电影级别彩虹颜色...")
for i in range(total_points):
    color = _calculate_cinematic_rainbow_color(i, total_points)
    # 将ManimGL颜色转换为RGB数组
    rgb = color_to_rgb(color)
    cinematic_colors[i] = [rgb[0], rgb[1], rgb[2]]

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
            opacity_fade=(1.0, 0.0),  # 使用计算的透明度
            width_fade=(avg_width_start, avg_width_end),  # 使用计算的宽度
            glow_factor=1.0,            # 使用平均辉光强度
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
            if self.frame_count % 30 == 0:  # 每1秒更新一次颜色
                updated_colors = cinematic_colors.to_numpy()
                rgba_colors = np.column_stack([updated_colors, np.ones(total_points)])
                self.dot_cloud.data['rgba'] = rgba_colors
            
            # 5. GPU shader并行更新所有轨迹（已经是最优化的）
            self.multi_tails.update_all_tails(dt)
        
        # 添加超高性能更新器
        self.dot_cloud.add_updater(ultra_high_performance_updater)
        
        # 电影级别的运镜设置
        self.setup_camera_movement()
        # # 添加粒子跟踪效果
        # self.add_particle_tracking()
        
        # # 清理
        # self.dot_cloud.clear_updaters()
        
        # 性能报告
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\\n=== 性能报告 ===")
        print(f"总时间: {total_time:.2f}秒")
        print(f"总帧数: {self.frame_count}")
        print(f"平均FPS: {self.frame_count/total_time:.2f}")
        print(f"粒子数: {total_points}")
        print(f"每秒处理粒子数: {self.frame_count * total_points / total_time:.0f}")

    def setup_camera_movement(self):
        """电影级别的运镜设置 - 参考cardioid_reference.py"""
        # [运镜一] 初始俯视：从顶部观察整体结构 (5秒)
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=45 * DEGREES,
                phi=60 * DEGREES
            ).set_height(16),
            run_time=5,
            rate_func=lambda t:smooth(smooth(t))
        )

        # [运镜二] 俯冲并翻滚：扫过底部，朝向背面 (8秒)
        # # 这是一个复杂的运镜，包含大的角度变化，因此放慢速度
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=135 * DEGREES,
        #         phi=-70 * DEGREES
        #     ).set_height(15),
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

        # # [运镜三] 侧向漂移：从背面掠过左侧 (7秒)
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=240 * DEGREES,
        #         phi=30 * DEGREES
        #     ),
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

        # # [运镜四] 垂直拉升与旋转：经过顶部，朝向正面 (8秒)
        # # 大幅度垂直视角变化，速度放慢
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=350 * DEGREES,
        #         phi=80 * DEGREES,
        #     ).set_height(18),
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

        # # [运镜五] 螺旋式后退：全景展示 (7秒)
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=400 * DEGREES, # 增加一圈多的旋转
        #         phi=45 * DEGREES
        #     ).set_height(25), # 拉远镜头
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

        # # [运镜六] "荷兰角"推近：创造不稳定感 (8秒)
        # # 从远处推近，同时伴随旋转，需要较长时间来展现过程
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=430 * DEGREES,
        #         phi=20 * DEGREES,
        #         gamma=25 * DEGREES  # 倾斜相机，制造荷兰角
        #     ).set_height(10), # 推近镜头
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

        # # [运镜七] 归正与环绕：恢复稳定，环视正面 (7秒)
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=480 * DEGREES,
        #         phi=40 * DEGREES,
        #         gamma=0 * DEGREES # 恢复水平
        #     ),
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

        # # 回到正面
        # self.play(
        #     self.camera.frame.animate.set_euler_angles(
        #         theta=0 * DEGREES,
        #         phi=0 * DEGREES,
        #         gamma=0 * DEGREES # 恢复水平
        #     ).set_height(32),
        #     run_time=5,
        #     rate_func=lambda t:smooth(smooth(t))
        # )

    def add_particle_tracking(self):
        """添加粒子跟踪效果 - 参考cardioid_reference.py"""
        # 选择一个特定的粒子进行跟踪 (选择中间位置的粒子)
        target_particle_index = 90 * 3 + 1  # 第90条曲线的第2个点

        # 创建跟踪器 - 发光点
        tracker_dot = GlowDot(
            center=self.dot_cloud.get_points()[target_particle_index],
            radius=0.08,
            color=ORANGE,
            glow_factor=1
        )
        self.add(tracker_dot)

        # 让tracker跟随目标粒子移动
        def update_tracker(tracker):
            points = self.dot_cloud.get_points()
            if target_particle_index < len(points):
                tracker.move_to(points[target_particle_index])
            return tracker

        tracker_dot.add_updater(update_tracker)

        # 相机跟踪设置 - 平滑过渡到跟踪模式
        frame = self.camera.frame

        # 添加相机跟踪更新器
        def update_camera_tracking(camera_frame):
            camera_frame.move_to(tracker_dot.get_center())
            return camera_frame

        

        # 先平滑移动到目标粒子位置
        self.play(
            frame.animate.scale(0.125).move_to(tracker_dot.get_center()),
            run_time=2,
            rate_func=lambda t:smooth(smooth(t))
        )
        frame.add_updater(update_camera_tracking)
        # 跟踪阶段
        self.wait(3)  # 48秒运镜 + 4秒过渡 + 41秒跟踪 = 总共93秒

        # 清除所有跟踪相关的updater
        tracker_dot.clear_updaters()
        frame.clear_updaters()

        # 移除跟踪器
        self.remove(tracker_dot)

        # 恢复到原来的视角状态
        self.play(
            frame.animate.set_euler_angles(
                theta=0 * DEGREES,
                phi=0 * DEGREES
            ).scale(8).move_to(ORIGIN),
            run_time=2,
            rate_func=lambda t:smooth(smooth(t))
        )


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py ")
