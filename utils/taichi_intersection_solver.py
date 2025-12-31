# 这行代码导入了taichi库，taichi是一个用于高性能并行计算的Python库，常用于物理模拟和图形处理
import taichi as ti
# 这行代码导入了numpy库，numpy是Python中用于数值计算的强大库，提供数组和数学函数
import numpy as np
# 这行代码从manimlib库导入了所有内容，manimlib是Manim的库，用于创建数学动画
from manimlib import *

# 这行代码初始化了Taichi，使用GPU加速，这样可以让计算更快
ti.init(arch=ti.gpu)  # 使用 GPU 加速

# Taichi内核函数，用于并行计算两条曲线上最近点对（三维版本）
@ti.kernel
def find_closest_points_parallel_3d(
    # 参数：曲线A的点（三维）
    curve_a_points: ti.types.ndarray(dtype=ti.f32, ndim=2),
    # 参数：曲线B的点（三维）
    curve_b_points: ti.types.ndarray(dtype=ti.f32, ndim=2),
    # 参数：存储最小距离的数组
    min_distances: ti.types.ndarray(dtype=ti.f32, ndim=1),
    # 参数：存储最近点对索引的数组
    closest_pairs: ti.types.ndarray(dtype=ti.i32, ndim=2)
):
    """
    并行计算两条曲线上最近点对（三维空间）
    """
    # 循环遍历曲线A的所有点
    for i in range(curve_a_points.shape[0]):
        # 初始化最小距离为一个很大的数
        min_dist = 1e10
        # 初始化最近的B点索引为-1
        closest_b_idx = -1
        
        # 循环遍历曲线B的所有点
        for j in range(curve_b_points.shape[0]):
            # 计算两点之间的x、y、z差
            dx = curve_a_points[i, 0] - curve_b_points[j, 0]
            dy = curve_a_points[i, 1] - curve_b_points[j, 1]
            dz = curve_a_points[i, 2] - curve_b_points[j, 2]
            # 计算欧几里得距离（三维）
            dist = ti.sqrt(dx * dx + dy * dy + dz * dz)
            
            # 如果这个距离小于当前最小距离
            if dist < min_dist:
                # 更新最小距离
                min_dist = dist
                # 更新最近点索引
                closest_b_idx = j
        
        # 将最小距离存储到数组中
        min_distances[i] = min_dist
        # 存储点对：A点的索引和B点的索引
        closest_pairs[i, 0] = i
        closest_pairs[i, 1] = closest_b_idx

# 定义一个类，叫做UniversalIntersectionSolver，用于求解两条曲线的交点（三维空间）
class UniversalIntersectionSolver:
    """万能交点求解器（三维空间，仅支持closest_points方法）"""
    
    # 类的初始化方法，当创建对象时自动调用
    def __init__(self, tolerance=0.01, max_depth=8):
        # 设置容差值，用于判断交点
        self.tolerance = tolerance
        # max_depth 保留但在 closest_points 方法中不使用
        self.max_depth = max_depth
    
    # 定义一个方法，用于求解两条曲线的交点（仅支持closest_points方法，三维）
    def solve_intersections(self, curve_a, curve_b, method="closest_points"):
        """
        求解两条曲线的交点（三维空间）
        
        Args:
            curve_a, curve_b: 曲线对象（VMobject或ParametricCurve）
            method: 求解方法（仅支持 "closest_points"）
        
        Returns:
            交点列表（三维坐标）
        """
        # 只支持最近点方法
        if method == "closest_points":
            return self._closest_points_method_3d(curve_a, curve_b)
        else:
            raise ValueError("仅支持 'closest_points' 方法")
    
    # 定义最近点方法（三维版本）
    def _closest_points_method_3d(self, curve_a, curve_b):
        """最近点方法（三维空间）"""
        # 获取曲线A的点（包含xyz三个坐标）
        points_a = curve_a.get_points()[:, :3].astype(np.float32)
        # 获取曲线B的点（包含xyz三个坐标）
        points_b = curve_b.get_points()[:, :3].astype(np.float32)
        
        # 初始化最小距离数组
        min_distances = np.zeros(len(points_a), dtype=np.float32)
        # 初始化最近点对数组
        closest_pairs = np.zeros((len(points_a), 2), dtype=np.int32)
        
        # 调用Taichi内核函数计算最近点（三维版本）
        find_closest_points_parallel_3d(points_a, points_b, min_distances, closest_pairs)
        
        # 找到距离小于容差的点对
        intersections = []
        for i, dist in enumerate(min_distances):
            if dist < self.tolerance:
                # 获取A点的索引
                a_idx = closest_pairs[i, 0]
                # 获取B点的索引
                b_idx = closest_pairs[i, 1]
                # 取两点的中点作为交点（三维）
                intersection = (points_a[a_idx] + points_b[b_idx]) / 2
                # 添加到交点列表
                intersections.append(intersection)
        
        # 返回去重后的交点（三维）
        return self._remove_duplicates_3d(intersections)
    
    # 定义去除重复交点的方法（三维版本）
    def _remove_duplicates_3d(self, intersections):
        """去除重复的交点（三维空间）"""
        # 如果没有交点，返回空列表
        if not intersections:
            return []
        
        # 初始化唯一交点列表
        unique_intersections = [intersections[0]]
        # 遍历所有交点
        for point in intersections[1:]:
            is_duplicate = False
            # 检查是否与已有交点太近
            for existing in unique_intersections:
                if np.linalg.norm(point - existing) < self.tolerance:
                    is_duplicate = True
                    break
            # 如果不是重复的，添加
            if not is_duplicate:
                unique_intersections.append(point)
        
        # 返回唯一交点
        return unique_intersections

# 定义一个类，继承自Scene，用于创建动画演示
class MovingIntersectionDemo(Scene):
    # 定义construct方法，这是Manim场景的主要方法
    def construct(self):
        # 创建更复杂的测试曲线A，使用参数方程
        self.curve_a = ParametricCurve(
            # 参数方程：x = 2*cos(3t), y = 2*sin(2t)
            lambda t: np.array([2*np.cos(3*t), 2*np.sin(2*t), 0]),
            # t的范围从0到2π，步长0.0008，提高精度
            t_range=[0, 2*PI, 0.005],  # 提高精度：步长从0.005降到0.001
            # 设置颜色为红色
            color=RED
        )
        
        # 创建测试曲线B
        self.curve_b = ParametricCurve(
            # 参数方程：x = 1.5*cos(5t), y = 1.5*sin(4t)
            lambda t: np.array([1.5*np.cos(5*t), 1.5*np.sin(4*t), 0]),
            # 类似设置t范围和步长
            t_range=[0, 2*PI, 0.005],  # 提高精度：步长从0.005降到0.001
            # 设置颜色为蓝色
            color=BLUE
        )
        
        # 创建交点组，用于存储交点
        self.intersection_group = VGroup()
        # 初始化最后更新时间
        self.last_update_time = 0
        # 设置更新间隔，每0.1秒更新一次
        self.update_interval = 1/20  # 每0.1秒更新一次
        
        # 添加 updater 来实时更新交点
        self.intersection_group.add_updater(self.update_intersections)
        
        # 将曲线和交点组添加到场景
        self.add(self.curve_a, self.curve_b, self.intersection_group)
        
        # 显示初始曲线，使用动画
        self.play(ShowCreation(self.curve_a), ShowCreation(self.curve_b))
        
        # 连续移动曲线 B，并实时更新交点
        self.play(
            # 移动曲线B到右上
            self.curve_b.animate.shift(RIGHT * 2 + UP * 1),
            # 动画时间5秒
            run_time=5,
            # 使用线性速率函数
            rate_func=linear
        )
        
        # 暂停查看最终结果
        self.wait(2)
    
    # 定义更新交点的方法
    def update_intersections(self, group):
        # 控制更新频率，避免每帧都计算
        current_time = self.time
        if current_time - self.last_update_time < self.update_interval:
            return
        
        # 更新最后更新时间
        self.last_update_time = current_time
        
        # 清除旧交点
        group.clear()
       

        # tolerance一般要比t_range=[0, 2*PI, 0.005]中的0.005要大点，三倍最合适，max_depth一般设置为12
        #tolerance只适合closest_points的调参，max_depth只适合adaptive_grid
        solver = UniversalIntersectionSolver(tolerance=0.015, max_depth=1)
        # 求解交点，使用最近点方法
        intersections = solver.solve_intersections(self.curve_a, self.curve_b, "closest_points")
        
        # 添加新交点
        for point in intersections:
            # 创建黄色圆点表示交点
            dot = Dot(np.array([point[0], point[1], 0]), color=YELLOW, radius=0.05)
            # 添加到组
            group.add(dot)

# 如果这个文件被直接运行（不是被导入）
if __name__ == "__main__":
    # 运行Manim动画
    import os
    os.system("cd intersection_universal && manimgl taichi_intersection_solver.py MovingIntersectionDemo -w")
