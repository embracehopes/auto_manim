import taichi as ti
import numpy as np


import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from mobject.spherical_polyhedra_sphere import *
# --- 1. Taichi 设置 ---
ti.init(arch=ti.cpu)  # 使用原始设置

# 布料模拟参数 - 保持原始参数
n = 100  # 网格分辨率 (n x n 个顶点 = n*n 个点云总点数)
# 要改变点云密度：增加n获得更多点数，减少n获得更少点数
# 示例：n=64给出4096个点，n=256给出65536个点
quad_size = 1.0 / n
dt = 4e-2 / n
substeps = int(1 / 60 // dt)

gravity = ti.Vector([0, -9.8, 0])
spring_Y = 3e4
dashpot_damping = 1e4
drag_damping = 1

ball_radius = 0.3
ball_center = ti.Vector.field(3, dtype=float, shape=(1, ))
ball_center[0] = [0, 0, 0]

# 布料网格
x = ti.Vector.field(3, dtype=float, shape=(n, n))
v = ti.Vector.field(3, dtype=float, shape=(n, n))

# 网格索引和顶点
num_triangles = (n - 1) * (n - 1) * 2
indices = ti.field(int, shape=num_triangles * 3)
vertices = ti.Vector.field(3, dtype=float, shape=n * n)
colors = ti.Vector.field(3, dtype=float, shape=n * n)
# 添加RGBA颜色字段用于DotCloud
rgba_colors = ti.Vector.field(4, dtype=float, shape=n * n)

bending_springs = False

@ti.kernel
def initialize_mass_points():
    random_offset = ti.Vector([ti.random() - 0.5, ti.random() - 0.5]) * 0.1
    for i, j in x:
        x[i, j] = [
            i * quad_size - 0.5 + random_offset[0], 0.6,
            j * quad_size - 0.5 + random_offset[1]
        ]
        v[i, j] = [0, 0, 0]

@ti.kernel
def initialize_mesh_indices():
    for i, j in ti.ndrange(n - 1, n - 1):
        quad_id = (i * (n - 1)) + j
        # 第一个三角形
        indices[quad_id * 6 + 0] = i * n + j
        indices[quad_id * 6 + 1] = (i + 1) * n + j
        indices[quad_id * 6 + 2] = i * n + (j + 1)
        # 第二个三角形
        indices[quad_id * 6 + 3] = (i + 1) * n + j + 1
        indices[quad_id * 6 + 4] = i * n + (j + 1)
        indices[quad_id * 6 + 5] = (i + 1) * n + j

@ti.kernel
def compute_grid_colors():
    """使用Taichi计算网格状RGBA颜色"""
    for i, j in ti.ndrange(n, n):
        point_index = i * n + j
        if (i // 4 + j // 4) % 2 == 0:
            # 绿色网格
            rgba_colors[point_index] = ti.Vector([0.22, 0.72, 0.52, 1.0])
        else:
            # 红色网格
            rgba_colors[point_index] = ti.Vector([1.0, 0.334, 0.52, 1.0])

# 弹簧偏移量设置
spring_offsets = []
if bending_springs:
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (i, j) != (0, 0):
                spring_offsets.append(ti.Vector([i, j]))
else:
    for i in range(-2, 3):
        for j in range(-2, 3):
            if (i, j) != (0, 0) and abs(i) + abs(j) <= 2:
                spring_offsets.append(ti.Vector([i, j]))

@ti.kernel
def substep():
    # 重力
    for i in ti.grouped(x):
        v[i] += gravity * dt

    # 弹簧力
    for i in ti.grouped(x):
        force = ti.Vector([0.0, 0.0, 0.0])
        for spring_offset in ti.static(spring_offsets):
            j = i + spring_offset
            if 0 <= j[0] < n and 0 <= j[1] < n:
                x_ij = x[i] - x[j]
                v_ij = v[i] - v[j]
                d = x_ij.normalized()
                current_dist = x_ij.norm()
                original_dist = quad_size * float(i - j).norm()
                # 弹簧力
                force += -spring_Y * d * (current_dist / original_dist - 1)
                # 阻尼力
                force += -v_ij.dot(d) * d * dashpot_damping * quad_size

        v[i] += force * dt

    # 碰撞检测与响应
    for i in ti.grouped(x):
        v[i] *= ti.exp(-drag_damping * dt)
        offset_to_center = x[i] - ball_center[0]
        if offset_to_center.norm() <= ball_radius:
            # 速度投影
            normal = offset_to_center.normalized()
            dot_product = v[i].dot(normal)
            if dot_product < 0:
                v[i] -= dot_product * normal
        x[i] += dt * v[i]

@ti.kernel
def update_vertices():
    for i, j in ti.ndrange(n, n):
        vertices[i * n + j] = x[i, j]

# --- 2. ManimGL 场景 ---

class ClothSimulationScene(ThreeDScene):
    """Taichi布料模拟与ManimGL结合的3D场景"""
    
    def construct(self):
        # 初始化Taichi模拟
        initialize_mesh_indices()
        initialize_mass_points()
        # 计算网格颜色
        compute_grid_colors()
        #  中心位置: (-0.01, 0.21, 0.00)
        #  视野高度: 1.21
        
        # 设置3D相机 - 模拟原始视角
        self.camera.frame.reorient(0,0,0,(0, 0.21, 0.00),height=1.21)
 

        self.current_time = 0.0
        

        self.ball_sphere = SphericalPolyhedraSphere(
            radius=ball_radius,
            brightness=40,
            resolution=(80, 80)  # 使用适中的分辨率
        )

        self.ball_sphere.move_to(ball_center.to_numpy()[0])
        self.add(self.ball_sphere)
        
        # 创建DotCloud对象来显示布料（使用所有n*n个顶点作为点云）
        update_vertices()  # 确保顶点数据是最新的
        
        # 使用Taichi计算的RGBA颜色创建DotCloud
        # 获取顶点位置和颜色数据
        points_data = vertices.to_numpy()
        colors_data = rgba_colors.to_numpy()
        
        # 创建带有预计算颜色的DotCloud
        self.sur = DotCloud(
            points=points_data,
            radius=0.004
        )
        
        # 手动设置RGBA数据到DotCloud
        # 创建符合DotCloud数据结构的数组
        num_points = len(points_data)
        self.sur.data = np.zeros(num_points, dtype=self.sur.data_dtype)
        self.sur.data['point'] = points_data
        self.sur.data['radius'] = np.full((num_points, 1), 0.002)
        self.sur.data['rgba'] = colors_data
        
        self.add(self.sur)
      
        # 启动更新循环（使用manimgl的updater机制）
        def physics_updater(mob, dt):
            self.current_time += dt
            
            # 重置布料位置（每1.5秒重置一次）
            if self.current_time > 1.5:
                initialize_mass_points()
                self.current_time = 0
            
            # 执行物理模拟步骤
            for _ in range(substeps):
                substep()
            
            # 更新顶点数据
            update_vertices()
            
            # 更新DotCloud位置和颜色（所有n*n个点同时更新）
            # 获取最新的顶点位置
            points_data = vertices.to_numpy()
            
            # 直接更新DotCloud的点位置
            self.sur.set_points(points_data)
        
        # 为Surface添加更新器
        self.sur.add_updater(physics_updater)
        
        # 播放动画
        self.wait(10)
        
        # 清理更新器
        self.sur.clear_updaters()
        self.embed()
# 辅助函数
def rgb_to_color(rgb_array):
    """将RGB数组转换为Manim颜色"""
    if np.allclose(rgb_array, [0.22, 0.72, 0.52]):
        return "#38B883"  # 绿色
    else:
        return "#FF5585"  # 红色
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")