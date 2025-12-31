#!/usr/bin/env python3

import numpy as np
from manimlib import *

# 导入现有的glass cube surfaces
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mobject.glass_cube_complex_surface import GlassCubeComplexSquare
from mobject.glass_cube_side_surface import GlassCubeSideSquare

class SimpleCubeTest(Scene):
    """简化的立方体测试，只显示6个面，不包含复杂的动画"""
    
    def construct(self):
        # 设置3D视角
        frame = self.camera.frame
        frame.set_euler_angles(theta=-20 * DEGREES, phi=20 * DEGREES)
        
        # 创建坐标轴
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1], 
            z_range=[-3, 3, 1],
            axis_config={"stroke_width": 1, "stroke_opacity": 0.5}
        )
        self.add(axes)
        
        # 标题
        title = Text("简化立方体测试", font_size=24)
        title.to_edge(UP)
        self.add(title)
        
        cube_size = 1.0
        
        # 只使用一种shader来排除shader差异的干扰
        # 使用Complex shader但改变透明度
        
        # 前面
        front_face = GlassCubeComplexSquare()
        front_face.move_to([0, 0, cube_size])
        
        # 后面  
        back_face = GlassCubeComplexSquare()
        back_face.rotate(PI, axis=UP)
        back_face.move_to([0, 0, -cube_size])
        
        # 右面
        right_face = GlassCubeComplexSquare()
        right_face.rotate(PI/2, axis=UP)
        right_face.move_to([cube_size, 0, 0])
        
        # 左面
        left_face = GlassCubeComplexSquare()
        left_face.rotate(-PI/2, axis=UP)
        left_face.move_to([-cube_size, 0, 0])
        
        # 上面
        top_face = GlassCubeComplexSquare()
        top_face.rotate(-PI/2, axis=RIGHT)
        top_face.move_to([0, cube_size, 0])
        
        # 下面
        bottom_face = GlassCubeComplexSquare()
        bottom_face.rotate(PI/2, axis=RIGHT)
        bottom_face.move_to([0, -cube_size, 0])
        
        # 添加所有面
        all_faces = [front_face, back_face, right_face, left_face, top_face, bottom_face]
        self.add(*all_faces)
        
        # 静态等待观察
        self.wait(5)
        
        # 简单旋转
        self.play(
            frame.animate.set_euler_angles(theta=0, phi=60*DEGREES),
            run_time=3
        )
        self.wait(3)


class AlphaTestCube(Scene):
    """测试透明度问题 - 逐个显示面"""
    
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(theta=-30 * DEGREES, phi=30 * DEGREES)
        
        # 创建坐标轴
        axes = ThreeDAxes(
            x_range=[-2, 2, 1],
            y_range=[-2, 2, 1], 
            z_range=[-2, 2, 1],
            axis_config={"stroke_width": 2, "stroke_opacity": 0.8}
        )
        self.add(axes)
        
        cube_size = 1.0
        
        # 逐个添加面，每个面等待一段时间
        faces_info = [
            ("前面", [0, 0, cube_size], None),
            ("后面", [0, 0, -cube_size], (PI, UP)),
            ("右面", [cube_size, 0, 0], (PI/2, UP)),
            ("左面", [-cube_size, 0, 0], (-PI/2, UP)),
            ("上面", [0, cube_size, 0], (-PI/2, RIGHT)),
            ("下面", [0, -cube_size, 0], (PI/2, RIGHT))
        ]
        
        for i, (name, position, rotation) in enumerate(faces_info):
            # 显示当前面的名称
            label = Text(f"添加{name}", font_size=30, color=YELLOW)
            label.to_edge(UP)
            if i > 0:
                self.remove(prev_label)
            self.add(label)
            prev_label = label
            
            # 创建面
            face = GlassCubeComplexSquare()
            if rotation:
                face.rotate(rotation[0], axis=rotation[1])
            face.move_to(position)
            
            self.add(face)
            self.wait(2)
        
        # 最终显示所有面
        final_label = Text("所有6个面已添加", font_size=30, color=GREEN)
        final_label.to_edge(UP)
        self.remove(prev_label)
        self.add(final_label)
        
        self.wait(5)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")
