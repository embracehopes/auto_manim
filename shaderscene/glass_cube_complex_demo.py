#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
from manimlib import *
from mobject.glass_cube_complex_surface import GlassCubeComplexSquare  # 用于上下底面
from mobject.glass_cube_side_surface import GlassCubeSideSquare        # 用于四个侧面

class GlassCubeComplexDemo(Scene):
    def construct(self):
        # 设置3D视角 - 改为正视角度
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=0 * DEGREES,    # 正视角度，不倾斜
            phi=0 * DEGREES,      # 正视角度，不旋转
        )
        
        # 手动拼装立方体：创建6个相同的正方形，调整为1:1:1比例
        faces = []
        
        # 使用1.0的距离，形成1:1:1的立方体
        cube_size = 1.0
        
        # Front face (正前方)
        front = GlassCubeComplexSquare()
        front.move_to(ORIGIN + OUT * cube_size)
        faces.append(front)
        
        # Back face (正后方)
        back = GlassCubeComplexSquare()
        back.rotate(PI, axis=UP)
        back.move_to(ORIGIN + IN * cube_size)
        faces.append(back)
        
        # Right face (正右方)
        right = GlassCubeComplexSquare()
        right.rotate(PI/2, axis=UP)
        right.move_to(ORIGIN + RIGHT * cube_size)
        faces.append(right)
        
        # Left face (正左方)
        left = GlassCubeComplexSquare()
        left.rotate(-PI/2, axis=UP)
        left.move_to(ORIGIN + LEFT * cube_size)
        faces.append(left)
        
        # Top face (正上方)
        top = GlassCubeComplexSquare()
        top.rotate(-PI/2, axis=RIGHT)
        top.move_to(ORIGIN + UP * cube_size)
        faces.append(top)
        
        # Bottom face (正下方)
        bottom = GlassCubeComplexSquare()
        bottom.rotate(PI/2, axis=RIGHT)
        bottom.move_to(ORIGIN + DOWN * cube_size)
        faces.append(bottom)
        
        # 组合成一个立方体
        cube = Group(*faces)
        
        # 添加坐标轴作为参考
        axes = ThreeDAxes(
            x_range=[-2, 2, 1],
            y_range=[-2, 2, 1], 
            z_range=[-2, 2, 1],
            axis_config={"stroke_width": 2}
        )
        axes.set_opacity(0.3)
        
        # 显示物体
        self.add(axes, cube)
        
        # 等待一段时间观察正视效果
        self.wait(3)
        
        # 然后慢慢调整视角查看所有面
        self.play(
            frame.animate.set_euler_angles(
                theta=-20 * DEGREES,
                phi=30 * DEGREES,
            ),
            run_time=4
        )
        
        self.wait(2)
        
        # 继续旋转查看其他面
        self.play(
            frame.animate.set_euler_angles(
                theta=45 * DEGREES,
                phi=45 * DEGREES,
            ),
            run_time=4
        )
        
        self.wait(3)

# 新增：专门测试所有面是否正确显示的演示
class GlassCubeComplexAllFacesDemo(Scene):
    """测试所有立方体面是否都能正确显示shader效果"""
    def construct(self):
        # 初始正视角度
        frame = self.camera.frame
        frame.set_euler_angles(theta=0, phi=0)
        
        # 创建1:1:1比例的立方体
        cube_size = 1.0
        faces = []
        
        # 创建所有6个面
        for i, (position, rotation_axis, rotation_angle, name) in enumerate([
            ([0, 0, cube_size], UP, 0, "Front"),
            ([0, 0, -cube_size], UP, PI, "Back"), 
            ([cube_size, 0, 0], UP, PI/2, "Right"),
            ([-cube_size, 0, 0], UP, -PI/2, "Left"),
            ([0, cube_size, 0], RIGHT, -PI/2, "Top"),
            ([0, -cube_size, 0], RIGHT, PI/2, "Bottom")
        ]):
            face = GlassCubeComplexSquare()
            face.rotate(rotation_angle, axis=rotation_axis)
            face.move_to(position)
            faces.append(face)
            
        cube = Group(*faces)
        
        # 添加标签以便识别各个面
        labels = VGroup()
        for i, name in enumerate(["Front", "Back", "Right", "Left", "Top", "Bottom"]):
            label = Text(name, font_size=24)
            if name == "Front":
                label.move_to([0, 0, cube_size + 0.5])
            elif name == "Back":
                label.move_to([0, 0, -cube_size - 0.5])
            elif name == "Right":
                label.move_to([cube_size + 0.5, 0, 0])
            elif name == "Left":
                label.move_to([-cube_size - 0.5, 0, 0])
            elif name == "Top":
                label.move_to([0, cube_size + 0.5, 0])
            elif name == "Bottom":
                label.move_to([0, -cube_size - 0.5, 0])
            labels.add(label)
        
        self.add(cube, labels)
        
        # 依次查看每个面
        camera_positions = [
            (0, 0, "Front face"),
            (180 * DEGREES, 0, "Back face"),
            (-90 * DEGREES, 0, "Right face"), 
            (90 * DEGREES, 0, "Left face"),
            (0, 90 * DEGREES, "Top face"),
            (0, -90 * DEGREES, "Bottom face")
        ]
        
        for phi, theta, description in camera_positions:
            self.play(
                frame.animate.set_euler_angles(theta=theta, phi=phi),
                run_time=2
            )
            self.wait(2)

class GlassCubeComplexStaticDemo(Scene):
    """静态展示，便于观察复杂3D玻璃立方体效果"""
    def construct(self):
        # 设置3D视角
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-20 * DEGREES,
            phi=60 * DEGREES,
        )
        
        # 手动拼装立方体：创建6个相同的正方形，手动定位到立方体的6个面
        faces = []
        
        # Front face (正前方)
        front = GlassCubeComplexSquare()
        front.move_to(ORIGIN + OUT * 1)
        faces.append(front)
        
        # Back face (正后方)
        back = GlassCubeComplexSquare()
        back.rotate(PI, axis=UP)
        back.move_to(ORIGIN + IN * 1)
        faces.append(back)
        
        # Right face (正右方)
        right = GlassCubeComplexSquare()
        right.rotate(PI/2, axis=UP)
        right.move_to(ORIGIN + RIGHT * 1)
        faces.append(right)
        
        # Left face (正左方)
        left = GlassCubeComplexSquare()
        left.rotate(-PI/2, axis=UP)
        left.move_to(ORIGIN + LEFT * 1)
        faces.append(left)
        
        # Top face (正上方)
        top = GlassCubeComplexSquare()
        top.rotate(-PI/2, axis=RIGHT)
        top.move_to(ORIGIN + UP * 1)
        faces.append(top)
        
        # Bottom face (正下方)
        bottom = GlassCubeComplexSquare()
        bottom.rotate(PI/2, axis=RIGHT)
        bottom.move_to(ORIGIN + DOWN * 1)
        faces.append(bottom)
        
        # 组合成一个立方体
        cube = Group(*faces)
        
        # 显示物体
        self.add(cube)
        
        # 等待观察效果
        self.wait(15)

class GlassCubeComplexSingleDemo(Scene):
    """单面展示，便于调试shader效果"""
    def construct(self):
        # 设置3D视角
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=0 * DEGREES,
            phi=0 * DEGREES,
        )
        
        # 创建单个面用于调试
        single_face = GlassCubeComplexSquare()
        
        # 显示物体
        self.add(single_face)
        
        # 等待观察效果
        self.wait(10)

class GlassCubePerfectDemo(Scene):
    """完美演示：使用两种mobject组成1:1:1立方体"""
    def construct(self):
        # 设置正视角度
        frame = self.camera.frame
        frame.set_euler_angles(theta=0, phi=0)
        
        # 创建标准1:1:1立方体
        cube_size = 1.0
        
        # =================================
        # 🔺 上下底面：使用正视shader
        # =================================
        top_bottom_faces = []
        
        # Top face (上底面) - 使用正视shader
        top_face = GlassCubeComplexSquare()  # 正视shader，适合俯视
        top_face.rotate(-PI/2, axis=RIGHT)   # 旋转90度成为水平面
        top_face.move_to([0, cube_size, 0])
        top_bottom_faces.append(top_face)
        
        # Bottom face (下底面) - 使用正视shader  
        bottom_face = GlassCubeComplexSquare()  # 正视shader，适合俯视
        bottom_face.rotate(PI/2, axis=RIGHT)    # 旋转-90度成为水平面
        bottom_face.move_to([0, -cube_size, 0])
        top_bottom_faces.append(bottom_face)
        
        # =================================
        # 🔲 四个侧面：使用侧视shader  
        # =================================
        side_faces = []
        
        # Front face (前侧面) - 使用侧视shader
        front_face = GlassCubeSideSquare()     # 侧视shader，适合侧视
        front_face.move_to([0, 0, cube_size])
        side_faces.append(front_face)
        
        # Back face (后侧面) - 使用侧视shader
        back_face = GlassCubeSideSquare()      # 侧视shader，适合侧视
        back_face.rotate(PI, axis=UP)          # 旋转180度
        back_face.move_to([0, 0, -cube_size])
        side_faces.append(back_face)
        
        # Right face (右侧面) - 使用侧视shader
        right_face = GlassCubeSideSquare()     # 侧视shader，适合侧视
        right_face.rotate(PI/2, axis=UP)       # 旋转90度
        right_face.move_to([cube_size, 0, 0])
        side_faces.append(right_face)
        
        # Left face (左侧面) - 使用侧视shader
        left_face = GlassCubeSideSquare()      # 侧视shader，适合侧视
        left_face.rotate(-PI/2, axis=UP)       # 旋转-90度
        left_face.move_to([-cube_size, 0, 0])
        side_faces.append(left_face)
        
        # =================================
        # 🎯 组合和显示
        # =================================
        # 分别创建两个组
        top_bottom_group = Group(*top_bottom_faces)  # 上下底面组
        side_group = Group(*side_faces)              # 侧面组
        complete_cube = Group(top_bottom_group, side_group)  # 完整立方体
        
        # 添加标签说明
        labels = VGroup(
            Text("Top/Bottom: Front-view shader", font_size=16, color=BLUE).move_to([0, 2.5, 0]),
            Text("4 Sides: Side-view shader", font_size=16, color=RED).move_to([0, 2.2, 0])
        )
        
        # 添加坐标轴
        axes = ThreeDAxes(
            x_range=[-2, 2, 1],
            y_range=[-2, 2, 1], 
            z_range=[-2, 2, 1],
            axis_config={"stroke_width": 1, "stroke_opacity": 0.3}
        )
        
        self.add(axes, complete_cube, labels)
        
        # =================================
        # 🎬 动画展示
        # =================================
        # 初始正视观察（能看到前侧面效果）
        self.wait(3)
        
        # 轻微上升角度观察上底面
        self.play(
            frame.animate.set_euler_angles(
                theta=-20 * DEGREES,  # 稍微向下看
                phi=0 * DEGREES,
            ),
            run_time=3
        )
        self.wait(2)
        
        # 侧面角度观察侧面效果
        self.play(
            frame.animate.set_euler_angles(
                theta=0 * DEGREES,
                phi=45 * DEGREES,     # 45度侧视角度
            ),
            run_time=3
        )
        self.wait(3)
        
        # 综合角度观察整体效果
        self.play(
            frame.animate.set_euler_angles(
                theta=-30 * DEGREES,
                phi=30 * DEGREES,
            ),
            run_time=3
        )
        self.wait(2)
        
        # 最终全方位观察
        self.play(
            frame.animate.set_euler_angles(
                theta=20 * DEGREES,
                phi=60 * DEGREES,
            ),
            run_time=3
        )
        self.wait(5)

# 新增：测试两种shader的演示
class GlassCubeTwoShadersTest(Scene):
    """测试演示：分别显示两种shader效果"""
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(theta=0, phi=0)
        
        # 左侧：正视shader效果
        front_face = GlassCubeComplexSquare()
        front_face.move_to([-2, 0, 0])
        front_label = Text("Front View Shader", font_size=20).move_to([-2, -1.5, 0])
        
        # 右侧：侧视shader效果  
        side_face = GlassCubeSideSquare()
        side_face.move_to([2, 0, 0])
        side_label = Text("Side View Shader", font_size=20).move_to([2, -1.5, 0])
        
        self.add(front_face, side_face, front_label, side_label)
        self.wait(5)
        
        # 轻微旋转观察效果
        self.play(
            frame.animate.set_euler_angles(theta=-15*DEGREES, phi=15*DEGREES),
            run_time=3
        )
        self.wait(3)

class GlassCubeMobjectComparison(Scene):
    """专门展示两种mobject的区别"""
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(theta=0, phi=0)
        
        # =================================
        # 左侧：正视mobject (用于上下底面)
        # =================================
        front_view_square = GlassCubeComplexSquare()
        front_view_square.move_to([-2.5, 0, 0])
        front_view_label = VGroup(
            Text("Front-view Mobject", font_size=18, color=BLUE),
            Text("(For Top/Bottom faces)", font_size=14, color=BLUE)
        ).arrange(DOWN, buff=0.1).move_to([-2.5, -1.8, 0])
        
        # =================================  
        # 右侧：侧视mobject (用于四个侧面)
        # =================================
        side_view_square = GlassCubeSideSquare()
        side_view_square.move_to([2.5, 0, 0])
        side_view_label = VGroup(
            Text("Side-view Mobject", font_size=18, color=RED),
            Text("(For 4 Side faces)", font_size=14, color=RED)
        ).arrange(DOWN, buff=0.1).move_to([2.5, -1.8, 0])
        
        # =================================
        # 中间：组合说明
        # =================================
        center_explanation = VGroup(
            Text("Perfect Glass Cube =", font_size=16),
            Text("2×Front-view + 4×Side-view", font_size=14, color=YELLOW)
        ).arrange(DOWN, buff=0.1).move_to([0, 1.5, 0])
        
        self.add(front_view_square, side_view_square)
        self.add(front_view_label, side_view_label, center_explanation)
        
        # 展示效果差异
        self.wait(4)
        
        # 轻微旋转观察
        self.play(
            frame.animate.set_euler_angles(theta=-15*DEGREES, phi=20*DEGREES),
            run_time=3
        )
        self.wait(3)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")