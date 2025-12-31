#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
from manimlib import *
from mobject.cube_enjoyer_surface import CubeEnjoyerSquare

class CubeEnjoyerDemo(Scene):
    def construct(self):
        # 设置3D视角
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-30 * DEGREES,
            phi=70 * DEGREES,
        )
        
        # 手动拼装立方体：创建6个相同的正方形，手动定位到立方体的6个面
        faces = []
        
        # Front face (正前方)
        front = CubeEnjoyerSquare()
        front.move_to(ORIGIN + OUT)
        faces.append(front)
        
        # Back face (正后方)
        back = CubeEnjoyerSquare()
        back.rotate(PI, axis=UP)
        back.move_to(ORIGIN + IN)
        faces.append(back)
        
        # Right face (正右方)
        right = CubeEnjoyerSquare()
        right.rotate(PI/2, axis=UP)
        right.move_to(ORIGIN + RIGHT)
        faces.append(right)
        
        # Left face (正左方)
        left = CubeEnjoyerSquare()
        left.rotate(-PI/2, axis=UP)
        left.move_to(ORIGIN + LEFT)
        faces.append(left)
        
        # Top face (正上方)
        top = CubeEnjoyerSquare()
        top.rotate(-PI/2, axis=RIGHT)
        top.move_to(ORIGIN + UP)
        faces.append(top)
        
        # Bottom face (正下方)
        bottom = CubeEnjoyerSquare()
        bottom.rotate(PI/2, axis=RIGHT)
        bottom.move_to(ORIGIN + DOWN)
        faces.append(bottom)
        
        # 组合成一个立方体
        cube = Group(*faces)
        
        # 添加坐标轴作为参考
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1], 
            z_range=[-3, 3, 1],
            axis_config={"stroke_width": 2}
        )
        axes.set_opacity(0.3)
        
        # 显示物体
        self.add(axes, cube)
        
        # 添加一些动画
        self.play(
            Rotate(cube, angle=PI, axis=UP, run_time=4),
            rate_func=linear
        )
        
        self.play(
            Rotate(cube, angle=PI, axis=RIGHT, run_time=4),
            rate_func=linear
        )
        
        # 改变相机角度观察不同面
        self.play(
            frame.animate.set_euler_angles(
                theta=30 * DEGREES,
                phi=45 * DEGREES,
            ),
            run_time=3
        )
        
        self.wait(2)

class CubeEnjoyerStaticDemo(Scene):
    """静态展示，便于观察各个面的效果"""
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
        front = CubeEnjoyerSquare()
        front.move_to(ORIGIN + OUT)
        faces.append(front)
        
        # Back face (正后方)
        back = CubeEnjoyerSquare()
        back.rotate(PI, axis=UP)
        back.move_to(ORIGIN + IN)
        faces.append(back)
        
        # Right face (正右方)
        right = CubeEnjoyerSquare()
        right.rotate(PI/2, axis=UP)
        right.move_to(ORIGIN + RIGHT)
        faces.append(right)
        
        # Left face (正左方)
        left = CubeEnjoyerSquare()
        left.rotate(-PI/2, axis=UP)
        left.move_to(ORIGIN + LEFT)
        faces.append(left)
        
        # Top face (正上方)
        top = CubeEnjoyerSquare()
        top.rotate(-PI/2, axis=RIGHT)
        top.move_to(ORIGIN + UP)
        faces.append(top)
        
        # Bottom face (正下方)
        bottom = CubeEnjoyerSquare()
        bottom.rotate(PI/2, axis=RIGHT)
        bottom.move_to(ORIGIN + DOWN)
        faces.append(bottom)
        
        # 组合成一个立方体
        cube = Group(*faces)
        
        # 显示物体
        self.add(cube)
        
        # 等待观察效果
        self.wait(10)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")