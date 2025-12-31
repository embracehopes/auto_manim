from manimlib import *
from copy import deepcopy
import sys
from pathlib import Path

# utils
get_angle = lambda c: np.angle(-c) + PI if not c/abs(c) == 1 else 0
convert_angle = lambda a: a if a>=0 else a + TAU
#
#["#000814","#001d3d","#003566","#ffc300","#ffd60a"]
class Compass(VGroup):

    CONFIG = {
        'stroke_color': GREY_D,
        'fill_color': "#e4fae0",  # 银色金属
        'stroke_width': 2.5,
        'leg_length': 3,
        'leg_width': 0.12,
        'r': 0.2,
        'depth_test': True,
        # 新增配置项
        'metal_color': "#f4e6b8",  # 金属主色
        'metal_dark': "#6B6D58",   # 金属暗部
        'metal_light': "#9cf9df",  # 金属亮部
        'joint_color': "#5DA8F3",  # 铰链金色
        'pen_tip_color': '#1E40AF', # 笔尖蓝色
        'needle_color': '#DC2626',  # 针尖红色
    }
    _STYLE_KEYS = ('stroke_color', 'fill_color', 'stroke_width', 'leg_length', 'leg_width', 'r', 
                   'metal_color', 'metal_dark', 'metal_light', 'joint_color', 'pen_tip_color', 'needle_color')

    def __init__(self, span=2.5,  **kwargs):
        
        config = dict(self.CONFIG)
        config.update(kwargs)
        for key in self._STYLE_KEYS:
            setattr(self, key, config.pop(key, self.CONFIG[key]))
        self.span = config.pop('span', span)
        depth_test = config.pop('depth_test', self.CONFIG['depth_test'])
        self.depth_test = depth_test
        super().__init__(depth_test=depth_test, **config)
        self.theta = 0
        self.create_compass()

    def create_compass(self):

        s, l, r, w = self.span, self.leg_length, self.r, self.leg_width
        ratio = np.clip(s / (2 * l), -1.0, 1.0)
        self.theta = np.arcsin(ratio)

        # 主铰链圆（金色，带光泽）
        self.c = Circle(
            radius=r, 
            fill_color=self.joint_color, 
            fill_opacity=0.95, 
            stroke_color=self.metal_dark, 
            stroke_width=self.stroke_width*3
        )
        
        # 内圈装饰（深色）
        c_inner = Circle(
            radius=r*0.6, 
            fill_color=self.metal_dark, 
            fill_opacity=0.8, 
            stroke_width=self.stroke_width*0.5,
            stroke_color=self.joint_color
        )
        
        # 外圈高光
        c2 = Circle(
            radius=r+self.stroke_width*3/100/2, 
            fill_opacity=0, 
            stroke_color=self.metal_light, 
            stroke_width=self.stroke_width*1.5
        )

        # 左腿（针脚）- 带金属渐变和细节
        # 主体
        leg_1_main = Polygon(
            ORIGIN, l * RIGHT, (l-w*np.sqrt(3)) * RIGHT + w * DOWN, w * DOWN,
            stroke_width=self.stroke_width*0.8, 
            stroke_color=self.metal_dark, 
            fill_color=self.metal_color,
            fill_opacity=0.95
        )
        # 高光条
        leg_1_highlight = Polygon(
            w*0.3 * DOWN, 
            (l-w*0.5) * RIGHT + w*0.3 * DOWN, 
            (l-w*0.5) * RIGHT + w*0.5 * DOWN,
            w*0.5 * DOWN,
            stroke_width=0, 
            fill_color=self.metal_light,
            fill_opacity=0.5
        )
        # 针尖（红色三角）
        needle_tip = Polygon(
            l * RIGHT, 
            (l+w*1.5) * RIGHT + w*0.1 * DOWN,
            (l+w*1.5) * RIGHT + w*0.1 * UP,
            stroke_width=self.stroke_width*0.5,
            stroke_color=self.metal_dark,
            fill_color=self.needle_color,
            fill_opacity=0.9
        )
        self.leg_1 = VGroup(leg_1_main, leg_1_highlight, needle_tip).rotate(
            -PI/2-self.theta, about_point=self.c.get_center()
        )

        # 右腿（笔脚）- 带金属渐变和笔尖
        # 主体
        leg_2_main = Polygon(
            ORIGIN, l * RIGHT, (l-w*np.sqrt(3)) * RIGHT + w * UP, w * UP,
            stroke_width=self.stroke_width*0.8, 
            stroke_color=self.metal_dark, 
            fill_color=self.metal_color,
            fill_opacity=0.95
        )
        # 高光条
        leg_2_highlight = Polygon(
            w*0.3 * UP, 
            (l-w*0.5) * RIGHT + w*0.3 * UP, 
            (l-w*0.5) * RIGHT + w*0.5 * UP,
            w*0.5 * UP,
            stroke_width=0, 
            fill_color=self.metal_light,
            fill_opacity=0.5
        )
        # 笔尖（蓝色圆锥形）
        pen_tip = Polygon(
            l * RIGHT, 
            (l+w*1.2) * RIGHT + w*0.1 * DOWN,
            (l+w*1.2) * RIGHT + w*0.1 * UP,
            stroke_width=self.stroke_width*0.5,
            stroke_color=self.metal_dark,
            fill_color=self.pen_tip_color,
            fill_opacity=0.9
        )
        # 笔芯（深蓝色）
        pen_core = Circle(
            radius=w*0.15,
            fill_color=BLUE_E,
            fill_opacity=1,
            stroke_width=0
        ).move_to((l+w*1.2) * RIGHT)
        
        self.leg_2 = VGroup(leg_2_main, leg_2_highlight, pen_tip, pen_core).rotate(
            -PI/2+self.theta, about_point=self.c.get_center()
        )

        # 手柄（顶部旋钮）
        h_rod = Line(
            UP * r, UP * (r + r * 1.8), 
            stroke_color=self.metal_color, 
            stroke_width=self.stroke_width*8
        )
        # 旋钮装饰纹理
        h_top = Circle(
            radius=r*1.1,
            fill_color=self.joint_color,
            fill_opacity=0.9,
            stroke_color=self.metal_dark,
            stroke_width=self.stroke_width*2
        ).move_to(UP * (r + r * 1.8))
        
        # 旋钮纹理线
        texture_lines = VGroup(*[
            Line(
                UP * (r + r * 1.8 - r*0.8), 
                UP * (r + r * 1.8 + r*0.8),
                stroke_width=self.stroke_width*0.5,
                stroke_color=self.metal_dark
            ).rotate(i * TAU / 8, about_point=UP * (r + r * 1.8))
            for i in range(8)
        ])

        self.head = VGroup(h_rod, h_top, texture_lines, self.c, c_inner, c2)
        self.add(self.leg_1, self.leg_2, self.head)
        self.move_to(ORIGIN)

        return self

    def _triangle_tip(self, triangle: Polygon) -> np.ndarray:
        vertices = triangle.get_vertices()
        if len(vertices) == 0:
            return triangle.get_center()
        reference = self.c.get_center()
        distances = [get_norm(v - reference) for v in vertices]
        max_dist = max(distances)
        farthest = [v for v, d in zip(vertices, distances) if abs(d - max_dist) < 1e-6]
        if len(farthest) == 1:
            return farthest[0]
        return np.mean(farthest, axis=0)

    def get_niddle_tip(self):
        return self._triangle_tip(self.leg_1[2])

    def get_pen_tip(self):
        return self._triangle_tip(self.leg_2[2])

    def move_niddle_tip_to(self, pos):
        self.shift(pos-self.get_niddle_tip())
        return self

    def rotate_about_niddle_tip(self, angle=PI/2):
        self.rotate(angle=angle, about_point=self.get_niddle_tip())

    def get_span(self):
        # return self.span 如果进行了缩放而self.span没变会有问题
        return get_norm(self.get_pen_tip() - self.get_niddle_tip())

    def set_span_by_angle(self, target_span):
        """通过迭代调整leg_2的角度，使实际pen_tip到niddle_tip的距离等于target_span"""
        current_span = self.get_span()
        if abs(current_span - target_span) < 0.001:
            return self
        
        # 计算需要的角度变化
        # 当前两腿的角度
        niddle = self.get_niddle_tip()
        pen = self.get_pen_tip()
        center = self.c.get_center()
        
        # leg_1 方向（从圆心到针尖）
        leg1_vec = niddle - center
        leg1_angle = np.angle(R3_to_complex(leg1_vec))
        
        # leg_2 方向（从圆心到笔尖）
        leg2_vec = pen - center
        leg2_angle = np.angle(R3_to_complex(leg2_vec))
        
        # 当前两腿夹角的一半
        current_half_angle = abs(leg2_angle - leg1_angle) / 2
        
        # 计算笔尖到圆心的距离（这是固定的）
        pen_to_center = get_norm(pen - center)
        niddle_to_center = get_norm(niddle - center)
        
        # 使用余弦定理计算需要的夹角
        # target_span^2 = pen_to_center^2 + niddle_to_center^2 - 2*pen_to_center*niddle_to_center*cos(angle)
        # cos(angle) = (pen_to_center^2 + niddle_to_center^2 - target_span^2) / (2*pen_to_center*niddle_to_center)
        cos_val = (pen_to_center**2 + niddle_to_center**2 - target_span**2) / (2 * pen_to_center * niddle_to_center + 1e-10)
        cos_val = np.clip(cos_val, -1.0, 1.0)
        target_full_angle = np.arccos(cos_val)
        
        # 需要旋转的角度（只旋转leg_2）
        current_full_angle = abs(leg2_angle - leg1_angle)
        angle_diff = target_full_angle - current_full_angle
        
        # 确定旋转方向：leg_2相对于leg_1的方向
        cross = np.cross(leg1_vec, leg2_vec)
        sign = 1 if cross[2] >= 0 else -1
        
        # 旋转leg_2
        self.leg_2.rotate(angle_diff * sign, about_point=center)
        # head也要旋转一半
        self.head.rotate(angle_diff * sign / 2, about_point=center)
        
        return self

    def set_span(self, s):
        return self.set_span_by_angle(s)

    def set_compass(self, center, pen_tip):
        # 1. 先移动针尖到center
        self.move_niddle_tip_to(center)
        
        # 2. 计算目标方向和距离
        target_vector = pen_tip - center
        target_span = get_norm(target_vector)
        target_angle = np.angle(R3_to_complex(target_vector))
        
        # 3. 调整span到目标距离
        self.set_span(target_span)
        
        # 4. 旋转整体使pen_tip对准目标方向
        # 移动后针尖可能偏移，重新定位
        self.move_niddle_tip_to(center)
        
        current_pen_tip = self.get_pen_tip()
        current_niddle = self.get_niddle_tip()
        current_angle = np.angle(R3_to_complex(current_pen_tip - current_niddle))
        angle_diff = target_angle - current_angle
        
        # 归一化角度差
        while angle_diff > PI:
            angle_diff -= TAU
        while angle_diff < -PI:
            angle_diff += TAU
        
        if abs(angle_diff) > 0.0001:
            self.rotate_about_niddle_tip(angle_diff)
        
        return self

    def set_compass_to_draw_arc(self, arc):
        return self.set_compass(arc.get_arc_center, arc.get_start())

    def reverse_tip(self):
        return self.flip(axis=self.head[0].get_end() - self.head[0].get_start(), about_point=self.c.get_center())

class Protractor(VGroup):
    """量角器类 - 高精度半透明设计"""
    
    CONFIG = {
        'radius': 3,
        'base_height': 0.4,             # 底座高度
        'stroke_width': 2.5,
        'stroke_color': '#1E3A8A',      # 深蓝色边框（与直角尺协调）
        'fill_color': '#DBEAFE',        # 淡蓝色主体（保持）
        'fill_opacity': 0.75,           # 半透明
        'scale_color': '#1E40AF',       # 深蓝色刻度（与直角尺一致）
        'number_color': '#1E3A8A',      # 深蓝色数字（加深）
        'inner_circle_color': '#60A5FA', # 亮蓝内圈颜色（保持）
        'center_color': '#3B82F6',      # 蓝色中心点（改为蓝色系）
        'edge_highlight': '#93C5FD',    # 浅蓝边缘高光（提亮）
        'arc_gradient_colors': [BLUE_C, BLUE_E, PURPLE_C],  # 弧线渐变色
        'arc_stroke_width': 4.5,        # 弧线粗细
        'depth_test': True,
    }
    
    def __init__(self, **kwargs):
        config = dict(self.CONFIG)
        config.update(kwargs)
        
        self.radius = config.pop('radius', self.CONFIG['radius'])
        self.base_height = config.pop('base_height', self.CONFIG['base_height'])
        self.stroke_width = config.pop('stroke_width', self.CONFIG['stroke_width'])
        self.stroke_color = config.pop('stroke_color', self.CONFIG['stroke_color'])
        self.fill_color = config.pop('fill_color', self.CONFIG['fill_color'])
        self.fill_opacity = config.pop('fill_opacity', self.CONFIG['fill_opacity'])
        self.scale_color = config.pop('scale_color', self.CONFIG['scale_color'])
        self.number_color = config.pop('number_color', self.CONFIG['number_color'])
        self.inner_circle_color = config.pop('inner_circle_color', self.CONFIG['inner_circle_color'])
        self.center_color = config.pop('center_color', self.CONFIG['center_color'])
        self.edge_highlight = config.pop('edge_highlight', self.CONFIG['edge_highlight'])
        self.arc_gradient_colors = config.pop('arc_gradient_colors', self.CONFIG['arc_gradient_colors'])
        self.arc_stroke_width = config.pop('arc_stroke_width', self.CONFIG['arc_stroke_width'])
        depth_test = config.pop('depth_test', self.CONFIG['depth_test'])
        
        super().__init__(depth_test=depth_test)
        self.create_protractor()
        # 量角器的测量中心点（刻度中心）
        self.measure_center = ORIGIN
    
    def create_protractor(self):
        """创建高精度量角器（带底座）"""
        r = self.radius
        h = self.base_height
        
        # 1. 主体半圆
        main_arc = Arc(
            start_angle=0,
            angle=PI,
            radius=r,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=0.9,
            fill_color=self.fill_color,
            fill_opacity=self.fill_opacity
        )
        
        # 2. 底座矩形（不包含上边线，与半圆闭合）
        # 矩形底边和两侧边
        base_rect = VGroup()
        # 底边
        bottom_line = Line(
            LEFT * r + DOWN * h, RIGHT * r + DOWN * h,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=0.9
        )
        # 左边
        left_line = Line(
            LEFT * r, LEFT * r + DOWN * h,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=0.9
        )
        # 右边
        right_line = Line(
            RIGHT * r, RIGHT * r + DOWN * h,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=0.9
        )
        # 填充
        base_fill = Rectangle(
            width=2*r,
            height=h,
            stroke_width=0,
            fill_color=self.fill_color,
            fill_opacity=self.fill_opacity
        ).shift(DOWN * h/2)
        
        base_rect.add(base_fill, bottom_line, left_line, right_line)
        
        # 内圈装饰圆（多层），最小的用于刻度线延伸的交点
        # 最小内圈半径为量角器的1/5
        inner_circles = VGroup()
        inner_radius_list = [0.9, 0.7, 0.2]  # 最小半径改为0.2（约1/5）
        for i, radius_scale in enumerate(inner_radius_list):
            inner_arc = Arc(
                start_angle=0,
                angle=PI,
                radius=r * radius_scale,
                stroke_width=self.stroke_width * 0.4 if i == 2 else self.stroke_width * 0.3,
                stroke_color=self.inner_circle_color,
                stroke_opacity=0.5 if i == 2 else 0.3 - i * 0.05  # 最小圆更明显
            )
            inner_circles.add(inner_arc)
        
        # 最小内圈半径（用于主刻度线延伸）
        min_inner_radius = r * inner_radius_list[-1]
        # 第二小内圈半径（主刻度线起点）
        second_inner_radius = r * inner_radius_list[-2]
        
        # 边缘高光效果
        edge_highlight = Arc(
            start_angle=0.1,
            angle=PI - 0.2,
            radius=r - 0.05,
            stroke_width=self.stroke_width * 0.6,
            stroke_color=self.edge_highlight,
            stroke_opacity=0.4
        )
        
        # 中心点标记（更精致）- 淡蓝色调
        center_dot = Dot(
            ORIGIN,
            radius=0.06,
            color="#006CFA",  # 淡蓝色中心点
            fill_opacity=1
        )
        
        center_ring = Circle(
            radius=0.1,
            stroke_width=self.stroke_width * 0.4,
            stroke_color="#0070F8",  # 亮蓝色中心圆环
            stroke_opacity=0.6,
            fill_opacity=0
        )
        
        # 中心十字线（更细）- 淡蓝色调
        cross_h = Line(
            LEFT * 0.12, RIGHT * 0.12,
            stroke_width=self.stroke_width * 0.5,
            stroke_color="#00FF37",  # 蓝色十字线
            stroke_opacity=0.7
        )
        cross_v = Line(
            UP * 0.12, DOWN * 0.12,
            stroke_width=self.stroke_width * 0.5,
            stroke_color="#FAE01D",  # 蓝色十字线
            stroke_opacity=0.7
        )
        
        # 刻度线和数字
        scales = VGroup()
        scale_numbers = VGroup()
        
        # 每10度一个主刻度（带数字，刻度线从第二小半圆延伸到最小半圆）
        for angle_deg in range(0, 181, 10):
            angle_rad = angle_deg * DEGREES
            # 主刻度线从第二小半圆开始
            start_point = np.array([second_inner_radius * np.cos(angle_rad), second_inner_radius * np.sin(angle_rad), 0])
            # 延伸到最小内圈（重合）
            end_point = np.array([min_inner_radius * np.cos(angle_rad), min_inner_radius * np.sin(angle_rad), 0])
            
            # 主刻度线（从第二小圆到最小圆）
            scale_line = Line(
                start_point, end_point,
                stroke_width=self.stroke_width * 0.7,
                stroke_color=self.scale_color,
                stroke_opacity=1
            )
            scales.add(scale_line)
            
            # 每10度标注数字（在第二小圆外侧）
            num_pos = np.array([(second_inner_radius + 0.3) * np.cos(angle_rad), (second_inner_radius + 0.3) * np.sin(angle_rad), 0])
            num_text = Text(
                str(angle_deg),
                font_size=14,
                color=self.number_color,
                font="Arial"
            ).move_to(num_pos).set_stroke(width=0)
            num_text.set_color(BLUE)
            scale_numbers.add(num_text)
        
        # 每5度一个次刻度（不标注数字，跳过主刻度）
        for angle_deg in range(0, 181, 5):
            if angle_deg % 10 != 0:
                angle_rad = angle_deg * DEGREES
                start_point = np.array([r * np.cos(angle_rad), r * np.sin(angle_rad), 0])
                end_point = np.array([(r - 0.12) * np.cos(angle_rad), (r - 0.12) * np.sin(angle_rad), 0])
                
                # 次刻度线（中等长度）
                scale_line = Line(
                    start_point, end_point,
                    stroke_width=self.stroke_width * 0.5,
                    stroke_color=self.scale_color,
                    stroke_opacity=0.65
                )
                scales.add(scale_line)
        
        # 每1度一个微刻度（不标注数字，非常细短）
        for angle_deg in range(0, 181, 1):
            if angle_deg % 5 != 0:
                angle_rad = angle_deg * DEGREES
                start_point = np.array([r * np.cos(angle_rad), r * np.sin(angle_rad), 0])
                end_point = np.array([(r - 0.06) * np.cos(angle_rad), (r - 0.06) * np.sin(angle_rad), 0])
                
                # 微刻度线（最短）
                scale_line = Line(
                    start_point, end_point,
                    stroke_width=self.stroke_width * 0.25,
                    stroke_color=self.scale_color,
                    stroke_opacity=0.4
                )
                scales.add(scale_line)
        
        # 组合所有元素
        self.main_arc = main_arc
        self.base_rect = base_rect
        self.inner_circles = inner_circles
        self.edge_highlight = edge_highlight
        self.center_mark = VGroup(center_dot, center_ring, cross_h, cross_v)
        self.scales = scales
        self.scale_numbers = scale_numbers
        
        self.add(main_arc, base_rect, inner_circles, edge_highlight, scales, scale_numbers, self.center_mark)
        return self
    
    def get_measure_center(self):
        """获取量角器的测量中心点（刻度中心）"""
        return self.measure_center
    
    def get_center(self):
        """获取量角器几何中心点"""
        return self.get_center_of_mass()
    
    def align_to_angle(self, start_point, end_point, center=None):
        """对齐量角器到指定角度
        start_point: 角度起始边上的点
        end_point: 角度终止边上的点
        center: 角的顶点（如果为None，使用当前中心）
        """
        if center is not None:
            self.move_to(center)
        
        # 计算需要旋转的角度
        angle = np.angle(R3_to_complex(start_point - self.get_center()))
        self.rotate(-angle, about_point=self.get_center())
        return self

class RightTriangle30(VGroup):
    """30°直角三角尺（30-60-90度）- 专业精致版"""
    
    CONFIG = {
        'length': 6,  # 斜边长度
        'stroke_width': 2.8,
        'stroke_color': '#2563EB',      # 更深的蓝色边框
        'fill_color': '#EFF6FF',        # 极淡蓝色主体（保持）
        'fill_opacity': 0.85,
        'scale_color': '#1E3A8A',       # 深蓝刻度（更深）
        'number_color': '#1E40AF',      # 深蓝数字
        'edge_color': '#60A5FA',        # 亮蓝边缘（增强对比）
        'right_angle_stroke_color': '#3B82F6',  # 直角标记边框颜色
        'right_angle_stroke_width': 2.2,        # 直角标记边框粗细（加粗）
        'right_angle_fill_color': '#DBEAFE',    # 直角标记填充颜色
        'right_angle_fill_opacity': 0.7,        # 直角标记填充透明度（提高）
        'depth_test': True,
    }
    
    def __init__(self, start_angle=0, **kwargs):
        """
        初始化30度直角尺
        
        参数:
            start_angle: 旋转角度（以度为单位），长边（斜边）作为参考边
                        默认0度时，直角顶点在原点，长边指向右侧
        """
        config = dict(self.CONFIG)
        config.update(kwargs)
        
        self.length = config.pop('length', self.CONFIG['length'])
        self.stroke_width = config.pop('stroke_width', self.CONFIG['stroke_width'])
        self.stroke_color = config.pop('stroke_color', self.CONFIG['stroke_color'])
        self.fill_color = config.pop('fill_color', self.CONFIG['fill_color'])
        self.fill_opacity = config.pop('fill_opacity', self.CONFIG['fill_opacity'])
        self.scale_color = config.pop('scale_color', self.CONFIG['scale_color'])
        self.number_color = config.pop('number_color', self.CONFIG['number_color'])
        self.edge_color = config.pop('edge_color', self.CONFIG['edge_color'])
        self.right_angle_stroke_color = config.pop('right_angle_stroke_color', self.CONFIG['right_angle_stroke_color'])
        self.right_angle_stroke_width = config.pop('right_angle_stroke_width', self.CONFIG['right_angle_stroke_width'])
        self.right_angle_fill_color = config.pop('right_angle_fill_color', self.CONFIG['right_angle_fill_color'])
        self.right_angle_fill_opacity = config.pop('right_angle_fill_opacity', self.CONFIG['right_angle_fill_opacity'])
        depth_test = config.pop('depth_test', self.CONFIG['depth_test'])
        
        self.start_angle = start_angle
        
        super().__init__(depth_test=depth_test)
        self.create_triangle()
    
    def create_triangle(self):
        """创建30-60-90度专业三角尺"""
        L = self.length
        
        # 30-60-90三角形的边长比例为 1:√3:2
        short_leg = L / 2
        long_leg = L * np.sqrt(3) / 2
        
        # 三个顶点
        vertex_right = ORIGIN
        vertex_bottom = DOWN * short_leg
        vertex_left = LEFT * long_leg
        
        # 主体三角形 - 填充白灰色（降低透明度）
        main_triangle = Polygon(
            vertex_right, vertex_bottom, vertex_left,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=0.95,
            fill_color='#F5F5F5',      # 白灰色填充
            fill_opacity=0.75          # 降低透明度（更不透明）
        )
        
        # 镂空形状（填充黑色模拟镂空效果）
        hollow_scale = 0.5  # 镂空三角形相对主体的缩放比例
        hollow_offset = (vertex_right + vertex_bottom + vertex_left) / 3 * 0.15  # 向中心微偏移
        
        hollow_triangle = Polygon(
            vertex_right * hollow_scale + hollow_offset,
            vertex_bottom * hollow_scale + hollow_offset,
            vertex_left * hollow_scale + hollow_offset,
            stroke_width=self.stroke_width * 0.8,
            stroke_color=self.stroke_color,
            stroke_opacity=0.7,
            fill_color=BLACK,  # 黑色填充表示镂空
            fill_opacity=1.0   # 完全不透明以创建镂空效果
        )
        
        # 内部淡色装饰线（在镂空区域边缘）
        inner_lines = VGroup()
        for i in range(1, 3):
            scale = hollow_scale + i * 0.08
            inner_tri = Polygon(
                vertex_right * scale + hollow_offset,
                vertex_bottom * scale + hollow_offset,
                vertex_left * scale + hollow_offset,
                stroke_width=self.stroke_width * 0.2,
                stroke_color=self.edge_color,
                stroke_opacity=0.25,
                fill_opacity=0
            )
            inner_lines.add(inner_tri)
        
        # 边缘高光（更细更柔和）
        edges = VGroup(
            Line(vertex_right, vertex_bottom, stroke_width=self.stroke_width*0.5, stroke_color=self.edge_color, stroke_opacity=0.5),
            Line(vertex_bottom, vertex_left, stroke_width=self.stroke_width*0.5, stroke_color=self.edge_color, stroke_opacity=0.5),
            Line(vertex_left, vertex_right, stroke_width=self.stroke_width*0.5, stroke_color=self.edge_color, stroke_opacity=0.5)
        )
        
        # 直角标记（使用配置的颜色和样式）
        right_angle_size = 0.22
        right_angle_mark = Polygon(
            ORIGIN,
            DOWN * right_angle_size,
            DOWN * right_angle_size + LEFT * right_angle_size,
            LEFT * right_angle_size,
            stroke_width=self.right_angle_stroke_width,
            stroke_color=self.right_angle_stroke_color,
            stroke_opacity=0.8,
            fill_color=self.right_angle_fill_color,
            fill_opacity=self.right_angle_fill_opacity
        )
        
        # 三条边的刻度线（朝向内部，严格沿着边缘，消除顶点处刻度）
        scales = VGroup()
        
        # 定义最小距离阈值：离顶点太近的刻度线将被隐藏
        min_distance_threshold = 0.15
        
        # 1. 斜边刻度（从vertex_bottom到vertex_left）
        num_scales = 20
        for i in range(num_scales + 1):
            t = i / num_scales
            # 起始点：严格在斜边上
            point_on_edge = vertex_bottom + t * (vertex_left - vertex_bottom)
            
            # 计算到两端顶点的距离
            dist_to_bottom = np.linalg.norm(point_on_edge - vertex_bottom)
            dist_to_left = np.linalg.norm(point_on_edge - vertex_left)
            
            # 垂直于斜边，朝向内部的方向（归一化）
            edge_vec = vertex_left - vertex_bottom
            perp_dir = np.array([edge_vec[1], -edge_vec[0], 0])
            perp_dir = perp_dir / np.linalg.norm(perp_dir)
            
            if i % 5 == 0:  # 主刻度（每5个）
                length = 0.18
                width = self.stroke_width * 0.7
                opacity = 0.85
            elif i % 2 == 0:  # 次刻度（每2个）
                length = 0.12
                width = self.stroke_width * 0.45
                opacity = 0.65
            else:  # 微刻度
                length = 0.06
                width = self.stroke_width * 0.3
                opacity = 0.45
            
            # 如果距离任一顶点太近，设置透明度为0（隐藏）
            if dist_to_bottom < min_distance_threshold or dist_to_left < min_distance_threshold:
                opacity = 0
            
            scale_line = Line(
                point_on_edge, point_on_edge + perp_dir * length,
                stroke_width=width,
                stroke_color=self.scale_color,
                stroke_opacity=opacity
            )
            scales.add(scale_line)
        
        # 2. 短直角边刻度（从vertex_right到vertex_bottom，严格沿着边缘）
        num_short = 10
        for i in range(num_short + 1):
            t = i / num_short
            # 起始点：严格在短边上
            point_on_edge = vertex_right + t * (vertex_bottom - vertex_right)
            
            # 计算到两端顶点的距离
            dist_to_right = np.linalg.norm(point_on_edge - vertex_right)
            dist_to_bottom = np.linalg.norm(point_on_edge - vertex_bottom)
            
            if i % 4 == 0:  # 主刻度
                length = 0.15
                width = self.stroke_width * 0.6
                opacity = 0.8
            elif i % 2 == 0:  # 次刻度
                length = 0.10
                width = self.stroke_width * 0.4
                opacity = 0.6
            else:  # 微刻度
                length = 0.05
                width = self.stroke_width * 0.25
                opacity = 0.4
            
            # 如果距离任一顶点太近，设置透明度为0
            if dist_to_right < min_distance_threshold or dist_to_bottom < min_distance_threshold:
                opacity = 0
            
            scale_line = Line(
                point_on_edge, point_on_edge + LEFT * length,
                stroke_width=width,
                stroke_color=self.scale_color,
                stroke_opacity=opacity
            )
            scales.add(scale_line)
        
        # 3. 长直角边刻度（从vertex_right到vertex_left，严格沿着边缘）
        num_long = 16
        for i in range(num_long + 1):
            t = i / num_long
            # 起始点：严格在长边上
            point_on_edge = vertex_right + t * (vertex_left - vertex_right)
            
            # 计算到两端顶点的距离
            dist_to_right = np.linalg.norm(point_on_edge - vertex_right)
            dist_to_left = np.linalg.norm(point_on_edge - vertex_left)
            
            if i % 4 == 0:  # 主刻度
                length = 0.15
                width = self.stroke_width * 0.6
                opacity = 0.8
            elif i % 2 == 0:  # 次刻度
                length = 0.10
                width = self.stroke_width * 0.4
                opacity = 0.6
            else:  # 微刻度
                length = 0.05
                width = self.stroke_width * 0.25
                opacity = 0.4
            
            # 如果距离任一顶点太近，设置透明度为0
            if dist_to_right < min_distance_threshold or dist_to_left < min_distance_threshold:
                opacity = 0
            
            scale_line = Line(
                point_on_edge, point_on_edge + DOWN * length,  # 朝向下方（内部）
                stroke_width=width,
                stroke_color=self.scale_color,
                stroke_opacity=opacity
            )
            scales.add(scale_line)
        
        # 组合元素（注意顺序：先填充色，再刻度线，这样刻度线不会被遮住）
        self.main_body = main_triangle
        self.hollow = hollow_triangle
        self.inner_lines = inner_lines
        self.edges = edges
        self.right_angle_mark = right_angle_mark
        self.scales = scales
        
        self.add(main_triangle, hollow_triangle, inner_lines, edges, right_angle_mark, scales)
        
        # 应用旋转：以直角顶点为中心，旋转到指定角度
        if self.start_angle != 0:
            self.rotate(
                self.start_angle * DEGREES,
                about_point=self.get_right_angle_vertex()
            )
        
        return self
    
    def get_right_angle_vertex(self):
        """获取直角顶点位置"""
        return self.main_body.get_vertices()[0]
    
    def get_30_degree_vertex(self):
        """获取30度角顶点位置"""
        return self.main_body.get_vertices()[1]
    
    def get_60_degree_vertex(self):
        """获取60度角顶点位置"""
        return self.main_body.get_vertices()[2]

class RightTriangle45(VGroup):
    """45°直角三角尺（45-45-90度等腰直角三角形）- 专业精致版"""
    
    CONFIG = {
        'length': 5,  # 直角边长度
        'stroke_width': 2.8,
        'stroke_color': '#3B82F6',      # 蓝色边框（与30度尺协调）
        'fill_color': '#F0F9FF',        # 极淡蓝色主体（稍浅一点）
        'fill_opacity': 0.85,
        'scale_color': '#1E3A8A',       # 深蓝刻度（与30度尺一致）
        'number_color': '#1E40AF',      # 深蓝数字（与30度尺一致）
        'edge_color': '#60A5FA',        # 亮蓝边缘（与30度尺一致）
        'right_angle_stroke_color': '#3B82F6',  # 直角标记边框颜色
        'right_angle_stroke_width': 2.2,        # 直角标记边框粗细（加粗）
        'right_angle_fill_color': '#EFF6FF',    # 直角标记填充颜色
        'right_angle_fill_opacity': 0.7,        # 直角标记填充透明度（提高）
        'depth_test': True,
    }
    
    def __init__(self, start_angle=0, **kwargs):
        """
        初始化45度直角尺
        
        参数:
            start_angle: 旋转角度（以度为单位），长边（斜边）作为参考边
                        默认0度时，直角顶点在原点，斜边指向左下方
        """
        config = dict(self.CONFIG)
        config.update(kwargs)
        
        self.length = config.pop('length', self.CONFIG['length'])
        self.stroke_width = config.pop('stroke_width', self.CONFIG['stroke_width'])
        self.stroke_color = config.pop('stroke_color', self.CONFIG['stroke_color'])
        self.fill_color = config.pop('fill_color', self.CONFIG['fill_color'])
        self.fill_opacity = config.pop('fill_opacity', self.CONFIG['fill_opacity'])
        self.scale_color = config.pop('scale_color', self.CONFIG['scale_color'])
        self.number_color = config.pop('number_color', self.CONFIG['number_color'])
        self.edge_color = config.pop('edge_color', self.CONFIG['edge_color'])
        self.right_angle_stroke_color = config.pop('right_angle_stroke_color', self.CONFIG['right_angle_stroke_color'])
        self.right_angle_stroke_width = config.pop('right_angle_stroke_width', self.CONFIG['right_angle_stroke_width'])
        self.right_angle_fill_color = config.pop('right_angle_fill_color', self.CONFIG['right_angle_fill_color'])
        self.right_angle_fill_opacity = config.pop('right_angle_fill_opacity', self.CONFIG['right_angle_fill_opacity'])
        depth_test = config.pop('depth_test', self.CONFIG['depth_test'])
        
        self.start_angle = start_angle
        
        super().__init__(depth_test=depth_test)
        self.create_triangle()
    
    def create_triangle(self):
        """创建45-45-90度专业等腰直角三角尺"""
        L = self.length
        
        # 三个顶点
        vertex_right = ORIGIN
        vertex_bottom = DOWN * L
        vertex_left = LEFT * L
        
        # 主体三角形 - 填充白灰色（降低透明度）
        main_triangle = Polygon(
            vertex_right, vertex_bottom, vertex_left,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=0.95,
            fill_color='#F5F5F5',      # 白灰色填充
            fill_opacity=0.75          # 降低透明度（更不透明）
        )
        
        # 镂空形状（填充黑色模拟镂空效果）
        hollow_scale = 0.5  # 镂空三角形相对主体的缩放比例
        hollow_offset = (vertex_right + vertex_bottom + vertex_left) / 3 * 0.15  # 向中心微偏移
        
        hollow_triangle = Polygon(
            vertex_right * hollow_scale + hollow_offset,
            vertex_bottom * hollow_scale + hollow_offset,
            vertex_left * hollow_scale + hollow_offset,
            stroke_width=self.stroke_width * 0.8,
            stroke_color=self.stroke_color,
            stroke_opacity=0.7,
            fill_color=BLACK,  # 黑色填充表示镂空
            fill_opacity=1.0   # 完全不透明以创建镂空效果
        )
        
        # 内部淡色装饰线（在镂空区域边缘，等距平行线）
        inner_lines = VGroup()
        for i in range(1, 3):
            scale = hollow_scale + i * 0.08
            inner_tri = Polygon(
                vertex_right * scale + hollow_offset,
                vertex_bottom * scale + hollow_offset,
                vertex_left * scale + hollow_offset,
                stroke_width=self.stroke_width * 0.2,
                stroke_color=self.edge_color,
                stroke_opacity=0.25,
                fill_opacity=0
            )
            inner_lines.add(inner_tri)
        
        # 对角线装饰（淡淡的辅助线）
        diagonal_line = DashedLine(
            vertex_right, vertex_left + vertex_bottom - vertex_right,
            stroke_width=self.stroke_width * 0.15,
            stroke_color=self.edge_color,
            stroke_opacity=0.15,
            dash_length=0.1
        )
        
        # 边缘高光
        edges = VGroup(
            Line(vertex_right, vertex_bottom, stroke_width=self.stroke_width*0.5, stroke_color=self.edge_color, stroke_opacity=0.5),
            Line(vertex_bottom, vertex_left, stroke_width=self.stroke_width*0.5, stroke_color=self.edge_color, stroke_opacity=0.5),
            Line(vertex_left, vertex_right, stroke_width=self.stroke_width*0.5, stroke_color=self.edge_color, stroke_opacity=0.5)
        )
        
        # 直角标记（使用配置的颜色和样式）
        right_angle_size = 0.25
        right_angle_mark = Polygon(
            ORIGIN,
            DOWN * right_angle_size,
            DOWN * right_angle_size + LEFT * right_angle_size,
            LEFT * right_angle_size,
            stroke_width=self.right_angle_stroke_width,
            stroke_color=self.right_angle_stroke_color,
            stroke_opacity=0.8,
            fill_color=self.right_angle_fill_color,
            fill_opacity=self.right_angle_fill_opacity
        )

        
        # 精细刻度线（朝向内部，严格沿着边缘，消除顶点处刻度）
        scales = VGroup()
        
        # 定义最小距离阈值：离顶点太近的刻度线将被隐藏
        min_distance_threshold = 0.15
        
        # 垂直边的刻度（从vertex_right到vertex_bottom，严格沿着边缘）
        num_vertical = 20
        for i in range(num_vertical + 1):
            t = i / num_vertical
            # 起始点：严格在垂直边上
            point_on_edge = vertex_right + t * (vertex_bottom - vertex_right)
            
            # 计算到两端顶点的距离
            dist_to_right = np.linalg.norm(point_on_edge - vertex_right)
            dist_to_bottom = np.linalg.norm(point_on_edge - vertex_bottom)
            
            if i % 5 == 0:  # 主刻度（每5个）
                length = 0.18
                width = self.stroke_width * 0.7
                opacity = 0.85
            elif i % 2 == 0:  # 次刻度（每2个）
                length = 0.12
                width = self.stroke_width * 0.45
                opacity = 0.65
            else:  # 微刻度
                length = 0.06
                width = self.stroke_width * 0.3
                opacity = 0.45
            
            # 如果距离任一顶点太近，设置透明度为0
            if dist_to_right < min_distance_threshold or dist_to_bottom < min_distance_threshold:
                opacity = 0
            
            scale_line = Line(
                point_on_edge, point_on_edge + LEFT * length,  # 朝向左侧（内部）
                stroke_width=width,
                stroke_color=self.scale_color,
                stroke_opacity=opacity
            )
            scales.add(scale_line)
        
        # 水平边的刻度（从vertex_right到vertex_left，严格沿着边缘）
        num_horizontal = 20
        for i in range(num_horizontal + 1):
            t = i / num_horizontal
            # 起始点：严格在水平边上
            point_on_edge = vertex_right + t * (vertex_left - vertex_right)
            
            # 计算到两端顶点的距离
            dist_to_right = np.linalg.norm(point_on_edge - vertex_right)
            dist_to_left = np.linalg.norm(point_on_edge - vertex_left)
            
            if i % 5 == 0:  # 主刻度（每5个）
                length = 0.18
                width = self.stroke_width * 0.7
                opacity = 0.85
            elif i % 2 == 0:  # 次刻度（每2个）
                length = 0.12
                width = self.stroke_width * 0.45
                opacity = 0.65
            else:  # 微刻度
                length = 0.06
                width = self.stroke_width * 0.3
                opacity = 0.45
            
            # 如果距离任一顶点太近，设置透明度为0
            if dist_to_right < min_distance_threshold or dist_to_left < min_distance_threshold:
                opacity = 0
            
            scale_line = Line(
                point_on_edge, point_on_edge + DOWN * length,  # 朝向下方（内部）
                stroke_width=width,
                stroke_color=self.scale_color,
                stroke_opacity=opacity
            )
            scales.add(scale_line)
        
        # 斜边刻度（从vertex_bottom到vertex_left，严格沿着边缘）
        num_diagonal = 14
        for i in range(num_diagonal + 1):
            t = i / num_diagonal
            # 起始点：严格在斜边上
            point_on_edge = vertex_bottom + t * (vertex_left - vertex_bottom)
            
            # 计算到两端顶点的距离
            dist_to_bottom = np.linalg.norm(point_on_edge - vertex_bottom)
            dist_to_left = np.linalg.norm(point_on_edge - vertex_left)
            
            # 垂直于斜边，朝向内部（归一化）
            edge_vec = vertex_left - vertex_bottom
            perp_dir = np.array([edge_vec[1], -edge_vec[0], 0])
            perp_dir = perp_dir / np.linalg.norm(perp_dir)
            
            if i % 4 == 0:  # 主刻度
                length = 0.18
                width = self.stroke_width * 0.6
                opacity = 0.8
            elif i % 2 == 0:  # 次刻度
                length = 0.12
                width = self.stroke_width * 0.4
                opacity = 0.6
            else:  # 微刻度
                length = 0.06
                width = self.stroke_width * 0.25
                opacity = 0.4
            
            # 如果距离任一顶点太近，设置透明度为0
            if dist_to_bottom < min_distance_threshold or dist_to_left < min_distance_threshold:
                opacity = 0
            
            scale_line = Line(
                point_on_edge, point_on_edge + perp_dir * length,
                stroke_width=width,
                stroke_color=self.scale_color,
                stroke_opacity=opacity
            )
            scales.add(scale_line)
        
        # 组合元素（注意顺序：先填充色，再刻度线）
        self.main_body = main_triangle
        self.hollow = hollow_triangle
        self.inner_lines = inner_lines
        self.diagonal_line = diagonal_line
        self.edges = edges
        self.right_angle_mark = right_angle_mark
        self.scales = scales
        
        self.add(main_triangle, hollow_triangle, inner_lines, diagonal_line, edges, right_angle_mark, scales)
        
        # 应用旋转：以直角顶点为中心，旋转到指定角度
        if self.start_angle != 0:
            self.rotate(
                self.start_angle * DEGREES,
                about_point=self.get_right_angle_vertex()
            )
        
        return self
        
        return self
    
    def get_right_angle_vertex(self):
        """获取直角顶点位置"""
        return self.main_body.get_vertices()[0]
    
    def get_45_degree_vertices(self):
        """获取两个45度角顶点位置"""
        return [self.main_body.get_vertices()[1], self.main_body.get_vertices()[2]]

class DrawingScene(InteractiveScene):

    CONFIG = {
        'compass_config':{
            'stroke_color': GREY_E,
            'fill_color': WHITE,
            'stroke_width': 2,
            'leg_length': 3,
            'leg_width': 0.12,
            'r': 0.2,
            'depth_test': True,
        }, # to define size and style of the compass
        'ruler_config':{
            'width': 10,
            'height': 0.8,
            'stroke_width': 3,
            'stroke_color': '#4B5563',  # 深灰色边框
            'stroke_opacity': 0.8,
            'fill_color': '#F3F4F6',    # 浅灰白色主体
            'fill_opacity': 0.95,
            'metal_edge_color': '#9CA3AF',  # 金属边缘
            'scale_color': '#1F2937',       # 刻度颜色
        }, # to define size and style of the ruler
        'dot_config':{
            'radius': 0.06,
            'color': GREY_E,
        }, # to define size and color of the dot (e.g., dot in arc/circle's center)
        'line_config':{
            'stroke_color': GREY_E,
            'stroke_width': 2.5,
        }, # the default line style drawing by ruler (not the defualt arc style drawing by compass)
        'brace_config':{
            'fill_color': GREY_E,
            'buff':0.025,
        },
        'text_config':{
            'size': 0.6 * 5, # 5 times than the actual size here and
                             # will be sacle down to the actual size later
                             # in 'get_length_label' methods.
            'font': 'Cambria Math',
            'color': GREY_E,
        },
        'add_ruler': False, # whether to add ruler into the scene at very begining
        # 弧线渐变配置
        'arc_gradient_colors': ["#2f00ff","#8900f2","#ffe600"],  # 弧线渐变颜色（从起点到终点）
        'arc_stroke_width': 4,  # 弧线粗细
    }

    def setup(self):
        # 首先调用父类InteractiveScene的setup方法，初始化必要的属性
        super().setup()
        
        config_source = getattr(self, 'CONFIG', {})
        defaults = DrawingScene.CONFIG

        if not hasattr(self, 'compass_config'):
            merged = deepcopy(defaults['compass_config'])
            merged.update(deepcopy(config_source.get('compass_config', {})))
            self.compass_config = merged
        if not hasattr(self, 'ruler_config'):
            merged = deepcopy(defaults['ruler_config'])
            merged.update(deepcopy(config_source.get('ruler_config', {})))
            self.ruler_config = merged
        if not hasattr(self, 'dot_config'):
            merged = deepcopy(defaults['dot_config'])
            merged.update(deepcopy(config_source.get('dot_config', {})))
            self.dot_config = merged
        if not hasattr(self, 'line_config'):
            merged = deepcopy(defaults['line_config'])
            merged.update(deepcopy(config_source.get('line_config', {})))
            self.line_config = merged
        if not hasattr(self, 'brace_config'):
            merged = deepcopy(defaults['brace_config'])
            merged.update(deepcopy(config_source.get('brace_config', {})))
            self.brace_config = merged
        if not hasattr(self, 'text_config'):
            merged = deepcopy(defaults['text_config'])
            merged.update(deepcopy(config_source.get('text_config', {})))
            self.text_config = merged
        if not hasattr(self, 'add_ruler'):
            self.add_ruler = config_source.get('add_ruler', defaults['add_ruler'])
        
        # 处理弧线渐变配置
        if not hasattr(self, 'arc_gradient_colors'):
            self.arc_gradient_colors = config_source.get('arc_gradient_colors', defaults['arc_gradient_colors'])
        if not hasattr(self, 'arc_stroke_width'):
            self.arc_stroke_width = config_source.get('arc_stroke_width', defaults['arc_stroke_width'])
        
        self.cp = Compass(**self.compass_config)
        # 创建改进的尺子
        self.ruler = self.create_enhanced_ruler()
        self.dot = Dot(**self.dot_config)
        
        # 创建量角器和三角尺（初始时不添加到场景）
        self.protractor = Protractor(radius=2.5)
        self.triangle_30 = RightTriangle30(length=4)
        self.triangle_45 = RightTriangle45(length=3.5)

        # 移动到屏幕外（同时更新量角器的测量中心）
        self.cp.move_to(UP * 10)
        self.protractor.shift(UP * 10)
        self.protractor.measure_center = self.protractor.measure_center + UP * 10
        self.triangle_30.move_to(UP * 10)
        self.triangle_45.move_to(UP * 10)
        
        if self.add_ruler:
            self.ruler.move_to(DOWN * 10)
            self.add(self.ruler)
        self.add(self.cp)

        self.temp_points = []
    
    def create_enhanced_ruler(self):
        """创建增强版尺子，带有刻度和金属质感"""
        rc = self.ruler_config
        
        # 主体矩形
        main_body = Rectangle(
            width=rc['width'],
            height=rc['height'],
            stroke_width=rc['stroke_width'],
            stroke_color=rc['stroke_color'],
            stroke_opacity=rc['stroke_opacity'],
            fill_color=rc['fill_color'],
            fill_opacity=rc['fill_opacity']
        ).round_corners(rc['height']/10)
        
        # 金属边缘高光
        edge_top = Line(
            LEFT * rc['width']/2 + UP * rc['height']/2.5,
            RIGHT * rc['width']/2 + UP * rc['height']/2.5,
            stroke_width=rc['stroke_width']*0.8,
            stroke_color=rc['metal_edge_color'],
            stroke_opacity=0.6
        )
        
        edge_bottom = Line(
            LEFT * rc['width']/2 + DOWN * rc['height']/2.5,
            RIGHT * rc['width']/2 + DOWN * rc['height']/2.5,
            stroke_width=rc['stroke_width']*0.8,
            stroke_color=rc['metal_edge_color'],
            stroke_opacity=0.4
        )
        
        # 添加刻度线
        scales = VGroup()
        num_major = 10  # 主刻度数
        num_minor = 50  # 次刻度数
        
        # 主刻度（长）
        for i in range(num_major + 1):
            x = -rc['width']/2 + i * rc['width'] / num_major
            scale_line = Line(
                UP * rc['height']/3,
                DOWN * rc['height']/3,
                stroke_width=rc['stroke_width']*0.6,
                stroke_color=rc['scale_color'],
                stroke_opacity=0.7
            ).move_to(RIGHT * x)
            scales.add(scale_line)
        
        # 次刻度（短）
        for i in range(num_minor + 1):
            if i % 5 != 0:  # 跳过主刻度位置
                x = -rc['width']/2 + i * rc['width'] / num_minor
                scale_line = Line(
                    UP * rc['height']/5,
                    DOWN * rc['height']/5,
                    stroke_width=rc['stroke_width']*0.3,
                    stroke_color=rc['scale_color'],
                    stroke_opacity=0.4
                ).move_to(RIGHT * x)
                scales.add(scale_line)
        
        # 中心线装饰
        center_line = Line(
            LEFT * rc['width']/2,
            RIGHT * rc['width']/2,
            stroke_width=rc['stroke_width']*0.2,
            stroke_color=rc['scale_color'],
            stroke_opacity=0.3
        )
        
        # 组合所有元素
        ruler_group = VGroup(main_body, edge_top, edge_bottom, center_line, scales)
        
        # 添加一个透明的大矩形作为交互区域（保持原有接口兼容）
        interaction_rect = Rectangle(
            width=rc['width'],
            height=rc['height'],
            fill_opacity=0,
            stroke_opacity=0
        )
        
        # 保存主体引用以便获取顶点
        self.ruler_body = main_body
        
        return VGroup(ruler_group, interaction_rect)
    
    def get_ruler_corners(self):
        """获取直尺的四个顶点位置
        
        返回:
            dict: 包含四个顶点的字典
                - 'top_left': 左上角
                - 'top_right': 右上角
                - 'bottom_left': 左下角
                - 'bottom_right': 右下角
        """
        if not hasattr(self, 'ruler_body'):
            # 如果没有ruler_body，使用ruler的第一个子对象
            ruler_body = self.ruler[0][0] if len(self.ruler) > 0 else self.ruler
        else:
            ruler_body = self.ruler_body
            
        vertices = ruler_body.get_vertices()
        
        # 矩形顶点顺序通常是：左下，右下，右上，左上
        return {
            'bottom_left': vertices[0],
            'bottom_right': vertices[1],
            'top_right': vertices[2],
            'top_left': vertices[3]
        }
    
    def get_ruler_center(self):
        """获取直尺的中心位置
        
        返回:
            np.ndarray: 中心点坐标
        """
        return self.ruler.get_center()
    
    def get_ruler_left_edge(self):
        """获取直尺左边缘的中心点"""
        corners = self.get_ruler_corners()
        return (corners['top_left'] + corners['bottom_left']) / 2
    
    def get_ruler_right_edge(self):
        """获取直尺右边缘的中心点"""
        corners = self.get_ruler_corners()
        return (corners['top_right'] + corners['bottom_right']) / 2

    def construct(self):

        self.add(self.cp)
        self.play(ApplyMethod(self.cp.move_niddle_tip_to, ORIGIN), run_time=1)
        self.wait(0.3)
        self.set_span(3.6, run_time=1, rate_func=smooth)
        self.wait(0.5)
        self.set_compass(DL * 0.5, UR * 0.5, run_time=1, rate_func=there_and_back)
        arc = Arc(color=GREY_E)
        self.set_compass_to_draw_arc(arc)
        self.draw_arc_by_compass(arc)

        self.wait()

    def set_span(self, s, run_time=1, rate_func=smooth):

        s_old = self.cp.get_span()
        n = int(run_time * 30)
        dt = 1/30
        t_series = np.linspace(1, n, n)/n
        # s_series = s_old + rate_func(t_series) * (s - s_old)
        s_series = [s_old + rate_func(t_series[i]) * (s - s_old) for i in range(n)]
        for i in range(n):
            self.cp.set_span(s_series[i])
            self.wait(dt)

    def set_compass_direction(self, start, end, run_time=1, rate_func=smooth):
        vect = end - start
        a = np.angle(R3_to_complex(vect))
        c_old, p_old = self.cp.get_niddle_tip(), self.cp.get_pen_tip()
        a_old = np.angle(R3_to_complex(p_old - c_old))
        n = int(run_time * 30)
        dt = 1/30
        t_series = np.linspace(1, n, n)/n
        c_series = [c_old + rate_func(t_series[i]) * (start - c_old) for i in range(n)]
        delta_a = (a - a_old)/n
        for i in range(n):
            self.bring_to_front(self.cp)
            self.cp.move_niddle_tip_to(c_series[i])
            self.cp.rotate_about_niddle_tip(delta_a)
            self.wait(dt)

    def set_compass(self, center, pen_tip, run_time=1, rate_func=smooth, emphasize_dot=False):
        if emphasize_dot:
            run_time -= 0.15
        c_old, p_old = self.cp.get_niddle_tip(), self.cp.get_pen_tip()
        n = int(run_time * 30)
        dt = 1/30
        t_series = np.linspace(1, n, n)/n
        # s_series = s_old + rate_func(t_series) * (s - s_old)
        c_series = [c_old + rate_func(t_series[i]) * (center - c_old) for i in range(n)]
        p_series = [p_old + rate_func(t_series[i]) * (pen_tip - p_old) for i in range(n)]

        for i in range(n):
            self.bring_to_front(self.cp)
            self.cp.set_compass(c_series[i], p_series[i])
            self.wait(dt)
        if emphasize_dot:
            self.emphasize_dot([center, pen_tip], run_time=0.15)

    def set_compass_(self, center, pen_tip, adjust_angle=0, run_time=1, rate_func=smooth, emphasize_dot=False):

        vect = center - pen_tip
        a = np.angle(R3_to_complex(vect)) + adjust_angle
        s = get_norm(vect)
        c_old, p_old, s_old = self.cp.get_niddle_tip(), self.cp.get_pen_tip(), self.cp.get_span()
        a_old = np.angle(R3_to_complex(p_old - c_old))
        if emphasize_dot:
            run_time -= 0.15
        n = int(run_time * 30)
        dt = 1/30
        t_series = np.linspace(1, n, n)/n
        c_series = [c_old + rate_func(t_series[i]) * (center - c_old) for i in range(n)]
        delta_a = (a - a_old)/n
        s_series = [s_old + rate_func(t_series[i]) * (s - s_old) for i in range(n)]

        for i in range(n):
            self.bring_to_front(self.cp)
            self.cp.move_niddle_tip_to(c_series[i])
            self.cp.rotate_about_niddle_tip(delta_a)
            self.cp.set_span(s_series[i])
            self.wait(dt)
        if emphasize_dot:
            self.emphasize_dot([center, pen_tip], run_time=0.15)

    def set_compass_to_draw_arc(self, arc, **kwargs):
        self.set_compass(arc.get_arc_center(), arc.get_start(), **kwargs)

    def set_compass_to_draw_arc_(self, arc, **kwargs):
        self.set_compass_(arc.get_arc_center(), arc.get_start(), **kwargs)

    def draw_arc_by_compass(self, arc, is_prepared=True, run_time=1, rate_func=smooth, reverse=False, add_center=False, apply_gradient=True, **kwargs):
        self.bring_to_front(self.cp)
        if not is_prepared: self.set_compass_to_draw_arc(arc, run_time=0.5)
        
        # 为弧线添加颜色渐变和加粗效果
        if apply_gradient:
            arc.set_stroke(width=self.arc_stroke_width)
            arc.set_color_by_gradient(*self.arc_gradient_colors)
        
        # Calculate arc angle from start and stop angles
        start_angle = arc.get_start_angle()
        stop_angle = arc.get_stop_angle()
        # Handle angle wrapping
        theta = stop_angle - start_angle
        if theta < 0:
            theta += TAU
        if reverse:
            theta = -theta
        
        self.play(
            Rotating(self.cp, angle=theta, about_point=self.cp.get_niddle_tip()), 
            ShowCreation(arc), 
            rate_func=rate_func, 
            run_time=run_time
        )
        
        if add_center:
            d = Dot(self.cp.get_niddle_tip(), **self.dot_config).scale(0.5)
            self.temp_points.append(d)
            self.add(d)

    def emphasize_dot(self, pos, add_dot=False, size=1.2, run_time=0.2, **kwargs):
        if type(pos) == list:
            d = VGroup(*[Dot(pos[i], radius=size/2, color=GREY_C, fill_opacity=0.25).scale(0.25) for i in range(len(pos))])
        else:
            d = Dot(pos, radius=size/2, color=GREY_C, fill_opacity=0.25).scale(0.25)
        self.add(d)
        if type(pos) == list:
            self.play(d[0].animate.scale(4), d[1].animate.scale(4), rate_func=linear, run_time=run_time)

        else:
            self.play(d.animate.scale(4), rate_func=linear, run_time=run_time)

        self.remove(d)
        if add_dot:
            if type(pos) == list:
                dot = VGroup(*[Dot(pos[i],**kwargs) for i in range(len(pos))])
            else:
                dot = Dot(pos, **kwargs)
            self.add(dot)
            return dot

    def set_ruler(self, pos1, pos2, run_time=1, rate_func=smooth):
        p1, p2 = self.ruler[-1].get_vertices()[1], self.ruler[-1].get_vertices()[0]
        c12 = (p1 + p2) / 2
        center = (pos1 + pos2)/2
        self.bring_to_front(self.ruler)
        self.play(self.ruler.animate.shift(center - c12), run_time=run_time/2, rate_func=rate_func)
        self.play(Rotating(self.ruler, angle=np.angle(R3_to_complex(pos2 - pos1)) - np.angle(R3_to_complex(p2 - p1)), about_point=center), run_time=run_time/2, rate_func=rate_func)

    def draw_line(self, pos1, pos2, is_prepared=True, run_time=1.2, rate_func=smooth, pre_time=0.8, apply_gradient=True):
        if not is_prepared: self.set_ruler(pos1, pos2, run_time=pre_time)
        self.dot.move_to(pos1)
        self.emphasize_dot(pos1, run_time=0.15)
        self.add(self.dot)
        l = Line(pos1, pos2, **self.line_config)
        
        # 应用渐变和加粗效果（参考圆规画弧）
        if apply_gradient:
            l.set_stroke(width=self.arc_stroke_width)
            l.set_color_by_gradient(*self.arc_gradient_colors)
        
        self.play(ShowCreation(l), self.dot.animate.move_to(pos2), run_time=run_time-0.3, rate_func=rate_func)
        self.emphasize_dot(pos2, run_time=0.15)
        self.remove(self.dot)
        return l

    def draw_line_(self, l, is_prepared=True, run_time=1.2, rate_func=smooth, apply_gradient=True):
        pos1, pos2 = l.get_start(), l.get_end()
        if not is_prepared: self.set_ruler(pos1, pos2, run_time=0.5)
        self.dot.move_to(pos1)
        self.emphasize_dot(pos1, run_time=0.15)
        self.add(self.dot)
        
        # 应用渐变和加粗效果（参考圆规画弧）
        if apply_gradient:
            l.set_stroke(width=self.arc_stroke_width)
            l.set_color_by_gradient(*self.arc_gradient_colors)
        
        self.play(ShowCreation(l), self.dot.animate.move_to(pos2), run_time=run_time-0.3, rate_func=rate_func)
        self.emphasize_dot(pos2, run_time=0.15)
        self.remove(self.dot)
        return l

    def put_aside_ruler(self, direction=DOWN, run_time=0.5):
        self.bring_to_front(self.ruler)
        self.play(self.ruler.animate.move_to(direction * 15), run_time=run_time)

    def put_aside_compass(self, direction=DOWN, run_time=0.5):
        self.bring_to_front(self.cp)
        self.play(self.cp.animate.move_to(direction * 15), run_time=run_time)
    
    def bring_in_protractor(self, position=ORIGIN, rotate_angle=0, run_time=0.8):
        """将量角器移入场景
        position: 量角器测量中心的位置
        rotate_angle: 量角器绕测量中心旋转的角度（度数）
        """
        self.add(self.protractor)
        self.bring_to_front(self.protractor)
        
        # 先移动测量中心到目标位置
        current_measure_center = self.protractor.measure_center
        shift_vector = position - current_measure_center
        
        # 移动整个量角器

        self.play(self.protractor.animate.shift(shift_vector),  run_time=run_time)
        self.protractor.measure_center = position
        
        # 如果需要旋转，绕测量中心旋转
        if rotate_angle != 0:
            self.play(
                Rotating(self.protractor, angle=rotate_angle * DEGREES, about_point=position),
                run_time=run_time
            )
        else:
            # 直接显示，不需要动画（因为已经shift到位了）
            self.wait(0.01)
        
        return self.protractor
    
    def put_aside_protractor(self, direction=DOWN, run_time=0.5):
        """将量角器移出场景"""
        self.bring_to_front(self.protractor)
        target_pos = direction * 15
        # 计算移动向量
        current_center = self.protractor.get_center()
        shift_vector = target_pos - current_center
        self.play(self.protractor.animate.shift(shift_vector), run_time=run_time)
        # 更新测量中心
        self.protractor.measure_center += shift_vector
    
    def measure_angle(self, vertex, start_point, end_point, run_time=1.5, show_time=1.5, apply_gradient=True):
        """使用量角器测量角度
        vertex: 角的顶点
        start_point: 角的起始边上的点
        end_point: 角的终止边上的点
        apply_gradient: 是否对测量弧应用渐变和加粗
        """
        # 移动量角器到角的位置（使用测量中心对齐顶点）
        self.bring_to_front(self.protractor)
        current_measure_center = self.protractor.measure_center
        shift_vector = vertex - current_measure_center
        
        if np.linalg.norm(shift_vector) > 0.01:  # 只有当距离足够大时才移动
            self.play(self.protractor.animate.shift(shift_vector), run_time=run_time*0.4)
            self.protractor.measure_center = vertex
        
        # 更新实际的测量中心位置（量角器移动后）
        actual_center = self.protractor.measure_center
        
        # 对齐量角器（让0度线对准start_point）
        angle_to_start = np.angle(R3_to_complex(start_point - actual_center))
        self.play(
            Rotating(self.protractor, angle=-angle_to_start, about_point=actual_center),
            run_time=run_time*0.6
        )
        
        # 计算角度值（end_point相对于start_point的角度）
        angle_start = np.angle(R3_to_complex(start_point - actual_center))
        angle_end = np.angle(R3_to_complex(end_point - actual_center))
        angle_diff = angle_end - angle_start
        
        # 转换为度数并确保在0-360范围内
        angle_deg = np.degrees(angle_diff)
        if angle_deg < 0:
            angle_deg += 360
        angle_deg = int(round(angle_deg))
        
        # 显示测量的角度弧（应用渐变和加粗）
        # 使用move_arc_center_to确保弧心在正确位置
        angle_arc = Arc(
            start_angle=0,
            angle=angle_deg*DEGREES,
            radius=1,  # 增大半径使其清晰可见
            arc_center=vertex  # 使用实际的测量中心
        ).scale(0.8,about_point=vertex)

        angle_arc.set_stroke(width=6)  # 加粗使其更明显
        angle_arc.set_color_by_gradient(*["#2f00ff","#8900f2","#ffe600"])
        
        # 应用渐变和加粗效果（使用量角器的配置）
        if apply_gradient:
            angle_arc.set_stroke(width=6)  # 加粗使其更明显
            angle_arc.set_color_by_gradient(*["#2f00ff","#8900f2","#ffe600"])
        else:
            angle_arc.set_stroke(width=5, color=YELLOW)
        
        # 角度标签（使用Tex，更明显的颜色）
        # 计算标签位置（放在弧的中间位置）
        mid_angle = angle_to_start + (angle_deg * DEGREES) / 2
        label_radius = 1.3
        label_pos = actual_center + label_radius * np.array([np.cos(mid_angle), np.sin(mid_angle), 0])
        
        angle_label = Tex(
            f"{angle_deg}^\\circ",
            font_size=40,
            color=YELLOW
        ).move_to(label_pos)
        angle_label.set_color(YELLOW)
        

        
        self.play(ShowCreation(angle_arc) , run_time=0.64)
        self.play(Indicate(angle_label,3,RED) , run_time=0.36)
        self.wait(show_time)
        self.play(FadeOut(angle_arc), FadeOut(angle_label), run_time=0.3)
        
        return angle_deg
    
    def bring_in_triangle_30(self, position=ORIGIN, anchor_point='right_angle', rotation_angle=180, run_time=0.8):
        """将30度三角尺移入场景
        
        参数:
            position: 目标位置
            anchor_point: 锚点选择，可选值:
                - 'right_angle' (默认): 直角顶点
                - '30_degree': 30度角顶点  
                - '60_degree': 60度角顶点
                - 'center': 几何中心
            rotation_angle: 旋转角度（度），长边作为参考边
            run_time: 动画时间
        """
        self.add(self.triangle_30)
        self.bring_to_front(self.triangle_30)
        
        # 先旋转到指定角度
        if rotation_angle != 0:
            current_angle = self.triangle_30.start_angle
            delta_angle = rotation_angle - current_angle
            self.triangle_30.rotate(
                delta_angle * DEGREES,
                about_point=self.triangle_30.get_right_angle_vertex()
            )
            self.triangle_30.start_angle = rotation_angle
        
        # 根据锚点计算偏移
        if anchor_point == 'right_angle':
            anchor_pos = self.triangle_30.get_right_angle_vertex()
        elif anchor_point == '30_degree':
            anchor_pos = self.triangle_30.get_30_degree_vertex()
        elif anchor_point == '60_degree':
            anchor_pos = self.triangle_30.get_60_degree_vertex()
        else:  # 'center'
            anchor_pos = self.triangle_30.get_center()
        
        # 移动到目标位置
        offset = position - anchor_pos
        self.play(self.triangle_30.animate.shift(offset), run_time=run_time)
        return self.triangle_30
    
    def put_aside_triangle_30(self, direction=DOWN, run_time=0.5):
        """将30度三角尺移出场景"""
        self.bring_to_front(self.triangle_30)
        self.play(self.triangle_30.animate.move_to(direction * 15), run_time=run_time)
    
    def bring_in_triangle_45(self, position=ORIGIN, anchor_point='right_angle', rotation_angle=180, run_time=0.8):
        """将45度三角尺移入场景
        
        参数:
            position: 目标位置
            anchor_point: 锚点选择，可选值:
                - 'right_angle' (默认): 直角顶点
                - '45_degree_1': 第一个45度角顶点（底部）
                - '45_degree_2': 第二个45度角顶点（左侧）
                - 'center': 几何中心
            rotation_angle: 旋转角度（度），斜边作为参考边
            run_time: 动画时间
        """
        self.add(self.triangle_45)
        self.bring_to_front(self.triangle_45)
        
        # 先旋转到指定角度
        if rotation_angle != 0:
            current_angle = self.triangle_45.start_angle
            delta_angle = rotation_angle - current_angle
            self.triangle_45.rotate(
                delta_angle * DEGREES,
                about_point=self.triangle_45.get_right_angle_vertex()
            )
            self.triangle_45.start_angle = rotation_angle
        
        # 根据锚点计算偏移
        if anchor_point == 'right_angle':
            anchor_pos = self.triangle_45.get_right_angle_vertex()
        elif anchor_point == '45_degree_1':
            anchor_pos = self.triangle_45.get_45_degree_vertices()[0]
        elif anchor_point == '45_degree_2':
            anchor_pos = self.triangle_45.get_45_degree_vertices()[1]
        else:  # 'center'
            anchor_pos = self.triangle_45.get_center()
        
        # 移动到目标位置
        offset = position - anchor_pos
        self.play(self.triangle_45.animate.shift(offset), run_time=run_time)
        return self.triangle_45
    
    def put_aside_triangle_45(self, direction=DOWN, run_time=0.5):
        """将45度三角尺移出场景"""
        self.bring_to_front(self.triangle_45)
        self.play(self.triangle_45.animate.move_to(direction * 15), run_time=run_time)
    
    def draw_line_with_triangle(self, triangle, start_pos, angle=0, length=3, run_time=1.2, apply_gradient=True):
        """使用三角尺画直线
        triangle: 使用的三角尺对象（self.triangle_30 或 self.triangle_45）
        start_pos: 起始位置
        angle: 旋转角度
        length: 线段长度
        apply_gradient: 是否应用渐变和加粗
        """
        # 旋转三角尺
        if angle != 0:
            self.play(
                Rotating(triangle, angle=angle * DEGREES, about_point=triangle.get_center()),
                run_time=run_time*0.3
            )
        
        # 计算线段终点
        end_pos = start_pos + length * np.array([np.cos(angle * DEGREES), np.sin(angle * DEGREES), 0])
        
        # 画线
        self.dot.move_to(start_pos)
        self.emphasize_dot(start_pos, run_time=0.15)
        self.add(self.dot)
        
        line = Line(start_pos, end_pos, **self.line_config)
        
        # 应用渐变和加粗效果（参考圆规画弧）
        if apply_gradient:
            line.set_stroke(width=self.arc_stroke_width)
            line.set_color_by_gradient(*self.arc_gradient_colors)
        
        self.play(
            ShowCreation(line), 
            self.dot.animate.move_to(end_pos), 
            run_time=run_time*0.6, 
            rate_func=smooth
        )
        
        self.emphasize_dot(end_pos, run_time=0.15)
        self.remove(self.dot)
        
        return line

    def get_length_label(self, p1, p2, text='', reverse_label=False, add_bg=False, bg_color=WHITE):
        l = Line(p1, p2)
        b = Brace(l, direction=complex_to_R3(np.exp(1j * (l.get_angle()+PI/2 * (1 -2 * float(reverse_label))))), **self.brace_config)
        t = Text(text, **self.text_config).scale(0.2)
        if add_bg:
            bg = SurroundingRectangle(t, fill_color=bg_color, fill_opacity=0.6, stroke_opacity=0).set_height(t.get_height() + 0.05, stretch=True).set_width(t.get_width() + 0.05, stretch=True)
            b.put_at_tip(bg, buff=0.0)
            b.put_at_tip(t, buff=0.05)
            return b, bg, t
        else:
            b.put_at_tip(t, buff=0.05)
            return b, t

    def set_compass_and_show_span(self, p1, p2, run_time=1, show_span_time=[0.4, 0.3, 0.9, 0.4], text='', reverse_label=False, add_bg=True, **kwargs):
        self.set_compass(p1, p2, run_time=run_time, **kwargs)
        bt = self.get_length_label(p1, p2, text=text, reverse_label=reverse_label, add_bg=add_bg)
        b, t = bt[0], bt[-1]
        st = show_span_time
        self.play(ShowCreation(b), run_time=st[0])
        if add_bg:
            self.add(bt[1])
            self.play(FadeIn(t), run_time=st[1])
        else:
            self.play(FadeIn(t), run_time=st[1])
        self.wait(st[2])
        self.play(FadeOut(VGroup(*bt)), run_time=st[3])
        return bt

    def set_compass_and_show_span_(self, p1, p2, run_time=1, show_span_time=[0.4, 0.3, 0.9, 0.4], text='', reverse_label=False, add_bg=True, **kwargs):
        self.set_compass_(p1, p2, run_time=run_time, **kwargs)
        bt = self.get_length_label(p1, p2, text=text, reverse_label=reverse_label)
        b, t = bt[0], bt[-1]
        st = show_span_time
        self.play(ShowCreation(b), run_time=st[0])
        if add_bg:
            self.add(bt[1])
            self.play(FadeIn(t), run_time=st[1])
        else:
            self.play(FadeIn(t), run_time=st[1])
        self.wait(st[2])
        self.play(FadeOut(VGroup(*bt)), run_time=st[3])
        return bt

    def highlight_on(self, *mobjects, to_front=True, stroke_config={'color': '#66CCFF', 'width': 4}, run_time=1, **kwargs):
        self.highlight = VGroup(*mobjects)
        self.play(self.highlight.animate.set_stroke(**stroke_config), run_time=run_time, **kwargs)
        if to_front:
            self.bring_to_front(self.highlight)
            self.bring_to_front(self.cp, self.ruler)

    def highlight_off(self, *mobjects):

        pass

    def show_arc_info(self, arc, time_list=[0.5, 0.2, 0.3]):

        c = arc.get_arc_center()
        # Calculate radius from arc center to start point
        ps, pe = arc.get_start(), arc.get_end()
        r = get_norm(ps - c)
        s = arc.get_start_angle()
        # Calculate angle
        stop_angle = arc.get_stop_angle()
        a = stop_angle - s
        if a < 0:
            a += TAU
        
        d_center = Dot(c, radius=0.08, color=PINK)
        r1, r2 = DashedLine(c, ps, stroke_width=3.5, stroke_color=PINK), DashedLine(c, pe , stroke_width=3.5, stroke_color=PINK)
        arc_new = Arc(start_angle=s, angle=a, radius=r, arc_center=c, stroke_width=8, stroke_color=RED)
        self.play(ShowCreation(arc_new), run_time=time_list[0])
        self.play(FadeIn(arc_new), run_time=time_list[1])
        self.play(ShowCreation(r1), ShowCreation(r2), run_time=time_list[2])

class CompassAndRulerScene(DrawingScene):

    # just rename `DrawingScene`
    pass