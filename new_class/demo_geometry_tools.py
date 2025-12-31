from manimlib import *
import sys
from pathlib import Path

# 添加 geo_utils 到路径
sys.path.append(str(Path(__file__).parent))
from ruler_compass import DrawingScene, Protractor, RightTriangle30, RightTriangle45

class ProtractorDemo(DrawingScene):
    """量角器演示场景"""
    
    def construct(self):
        # 添加标题

        # # 显示量角器（移动到原点）
        # print(f"量角器初始位置: {self.protractor.get_center()}")
        # print(f"量角器测量中心: {self.protractor.get_measure_center()}")
        # self.bring_in_protractor(position=ORIGIN, run_time=1)
        # print(f"量角器移入后位置: {self.protractor.get_center()}")
        # print(f"量角器移入后测量中心: {self.protractor.get_measure_center()}")
        # self.wait(1)
        
        # 创建一个角度来测量
        vertex = LEFT * 2 + DOWN * 0.5
        start_point = vertex + RIGHT * 2
        end_point = vertex + UP * 1.5 + RIGHT * 1.5
        
        # 画出角的两条边
        line1 = Line(vertex, start_point, stroke_width=3, stroke_color=BLUE)
        line2 = Line(vertex, end_point, stroke_width=3, stroke_color=BLUE)
        
        # 移出量角器，画线
        self.put_aside_protractor(direction=UP, run_time=0.6)
        self.play(ShowCreation(line1), ShowCreation(line2), run_time=1)
        self.wait(0.5)
        
        # 使用量角器测量角度
        self.bring_in_protractor(position=vertex, run_time=0.8)
        self.measure_angle(vertex, start_point, end_point, run_time=1.5, show_time=2)

        
        self.wait(1)
        # # self.embed()
        # angle_arc = Arc(
        #     start_angle=0,
        #     angle=45*DEGREES,
        #     radius=1,  # 增大半径使其清晰可见
        #     arc_center=vertex  # 使用实际的测量中心
        # )

        # angle_arc.set_stroke(width=6)  # 加粗使其更明显
        # angle_arc.set_color_by_gradient(*["#2f00ff","#8900f2","#ffe600"])
        # self.play(ShowCreation(angle_arc), run_time=1)
        # print(angle_arc.get_arc_center())




class Triangle30Demo(DrawingScene):
    """30度三角尺演示场景"""
    
    def construct(self):
        dot=Dot(ORIGIN,color=RED)
        self.play(Write(dot))

        
        # 显示30度三角尺
        self.bring_in_triangle_30(position=ORIGIN,anchor_point="60_degree", run_time=1)
        self.wait(1.5)
        
        # # 旋转展示
        # self.play(
        #     Rotating(self.triangle_30, angle=PI, about_point=ORIGIN),
        #     run_time=2,
        #     rate_func=smooth
        # )
        # self.wait(0.5)
        
        # # 移到一边
        # self.play(self.triangle_30.animate.shift(LEFT * 3), run_time=0.8)
        
        # # 使用30度三角尺画30度线
        # start_pos1 = RIGHT * 1
        # line1 = self.draw_line_with_triangle(
        #     self.triangle_30, 
        #     start_pos1, 
        #     angle=30, 
        #     length=3, 
        #     run_time=1.5
        # )
        
        # # 画60度线
        # start_pos2 = RIGHT * 1 + DOWN * 1.5
        # self.play(self.triangle_30.animate.move_to(start_pos2 + LEFT * 1.5), run_time=0.6)
        # line2 = self.draw_line_with_triangle(
        #     self.triangle_30, 
        #     start_pos2, 
        #     angle=60, 
        #     length=3, 
        #     run_time=1.5
        # )
        
        # self.wait(1)
        
        # # 移走三角尺
        # self.put_aside_triangle_30(direction=DOWN, run_time=0.8)
        
        # self.wait(1)
        # self.play(FadeOut(VGroup(line1, line2)))


class Triangle45Demo(DrawingScene):
    """45度三角尺演示场景"""
    
    def construct(self):
        title = Text("45°直角三角尺演示", font_size=36).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 显示45度三角尺
        self.bring_in_triangle_45(position=ORIGIN, run_time=1)
        self.wait(1.5)
        
        # 旋转展示
        self.play(
            Rotating(self.triangle_45, angle=-PI, about_point=ORIGIN),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # 移到左边
        self.play(self.triangle_45.animate.shift(LEFT * 3.5), run_time=0.8)
        
        # 使用45度三角尺画45度线
        start_pos1 = RIGHT * 0.5
        line1 = self.draw_line_with_triangle(
            self.triangle_45, 
            start_pos1, 
            angle=45, 
            length=3, 
            run_time=1.5
        )
        
        # 画135度线
        start_pos2 = RIGHT * 0.5 + DOWN * 1.5
        self.play(self.triangle_45.animate.move_to(start_pos2 + LEFT * 1.5), run_time=0.6)
        line2 = self.draw_line_with_triangle(
            self.triangle_45, 
            start_pos2, 
            angle=135, 
            length=3, 
            run_time=1.5
        )
        
        self.wait(1)
        
        # 移走三角尺
        self.put_aside_triangle_45(direction=UP, run_time=0.8)
        
        self.wait(1)
        self.play(FadeOut(VGroup(title, line1, line2)))


class CompleteGeometryToolsDemo(DrawingScene):
    """完整的几何工具演示"""
    
    CONFIG = {
        'add_ruler': True,
    }
    
    def construct(self):
        title = Text("几何工具完整演示", font_size=40, color=BLUE).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # ===== 第一部分：使用圆规画圆 =====
        subtitle1 = Text("1. 圆规画圆", font_size=28).next_to(title, DOWN)
        self.play(FadeIn(subtitle1))
        
        center = LEFT * 3
        radius = 1.5
        
        # 设置圆规
        self.set_compass(center, center + RIGHT * radius, run_time=1, emphasize_dot=True)
        self.wait(0.3)
        
        # 画圆
        circle = Circle(radius=radius, stroke_width=3, stroke_color=GREEN).move_to(center)
        self.draw_arc_by_compass(
            Arc(radius=radius, angle=TAU, arc_center=center, stroke_width=3, stroke_color=GREEN),
            run_time=2,
            add_center=True
        )
        
        self.wait(0.5)
        self.put_aside_compass(direction=UP, run_time=0.6)
        
        # ===== 第二部分：使用直尺画线 =====
        self.play(FadeOut(subtitle1))
        subtitle2 = Text("2. 直尺画线", font_size=28).next_to(title, DOWN)
        self.play(FadeIn(subtitle2))
        
        p1 = RIGHT * 0.5 + UP * 1
        p2 = RIGHT * 3 + DOWN * 0.5
        
        line = self.draw_line(p1, p2, is_prepared=False, run_time=1.5, pre_time=0.8)
        
        self.wait(0.5)
        self.put_aside_ruler(direction=DOWN, run_time=0.6)
        
        # ===== 第三部分：使用量角器测量 =====
        self.play(FadeOut(subtitle2))
        subtitle3 = Text("3. 量角器测量角度", font_size=28).next_to(title, DOWN)
        self.play(FadeIn(subtitle3))
        
        # 在圆上画一个角
        angle_vertex = center
        angle_start = center + RIGHT * radius
        angle_end = center + UP * radius * 0.8 + RIGHT * radius * 0.6
        
        angle_line1 = Line(angle_vertex, angle_start, stroke_width=3, stroke_color=YELLOW)
        angle_line2 = Line(angle_vertex, angle_end, stroke_width=3, stroke_color=YELLOW)
        
        self.play(ShowCreation(angle_line1), ShowCreation(angle_line2), run_time=0.8)
        
        self.bring_in_protractor(position=angle_vertex, run_time=0.8)
        measured_angle = self.measure_angle(angle_vertex, angle_start, angle_end, run_time=1.5, show_time=2)
        
        self.put_aside_protractor(direction=LEFT, run_time=0.6)
        
        # ===== 第四部分：使用30度三角尺 =====
        self.play(FadeOut(subtitle3))
        subtitle4 = Text("4. 30°三角尺画线", font_size=28).next_to(title, DOWN)
        self.play(FadeIn(subtitle4))
        
        self.bring_in_triangle_30(position=RIGHT * 4 + UP * 1.5, run_time=0.8)
        self.wait(0.3)
        
        tri_line = self.draw_line_with_triangle(
            self.triangle_30,
            RIGHT * 3 + UP * 0.5,
            angle=30,
            length=2,
            run_time=1.2
        )
        
        self.wait(0.5)
        self.put_aside_triangle_30(direction=RIGHT, run_time=0.6)
        
        # ===== 第五部分：使用45度三角尺 =====
        self.play(FadeOut(subtitle4))
        subtitle5 = Text("5. 45°三角尺画线", font_size=28).next_to(title, DOWN)
        self.play(FadeIn(subtitle5))
        
        self.bring_in_triangle_45(position=RIGHT * 4 + DOWN * 1, run_time=0.8)
        self.wait(0.3)
        
        tri_line2 = self.draw_line_with_triangle(
            self.triangle_45,
            RIGHT * 3 + DOWN * 1.5,
            angle=45,
            length=2,
            run_time=1.2
        )
        
        self.wait(0.5)
        self.put_aside_triangle_45(direction=RIGHT, run_time=0.6)
        
        # ===== 结束 =====
        self.play(FadeOut(subtitle5))
        end_text = Text("几何工具演示完成！", font_size=36, color=GREEN).move_to(ORIGIN)
        self.play(Write(end_text))
        self.wait(2)
        
        # 淡出所有
        all_objects = VGroup(
            title, end_text, circle, line, 
            angle_line1, angle_line2, tri_line, tri_line2
        )
        self.play(FadeOut(all_objects), *[FadeOut(dot) for dot in self.temp_points])
        self.wait(0.5)

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  CompleteGeometryToolsDemo")
    #ProtractorDemo
    #os.system(f"cd {script_dir} && manimgl {script_name}.py  ProtractorDemo")