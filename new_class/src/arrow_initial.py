from manimlib import *

# ========== 辉光效果 API ==========

def create_glow_group(mobject, glow_color=None, n_layers=8, scale_factor=1.3, 
                      glow_width=None, base_opacity=0.25, use_about_point=None):
    """
    通用辉光效果函数 - 通过复制多层 + 缩放 + 透明度实现
    
    参数:
        mobject: 要添加辉光效果的对象
        glow_color: 辉光颜色，默认使用对象本身的颜色
        n_layers: 辉光层数，越多越平滑
        scale_factor: 最外层的缩放倍数（1.0 = 无缩放）
        glow_width: 辉光线条宽度，None 则使用原始宽度
        base_opacity: 最外层的透明度
        use_about_point: 缩放中心点，None 则使用对象中心
    
    返回:
        VGroup: 包含所有辉光层和原始对象的组
    """
    glow_layers = VGroup()
    
    if glow_color is None:
        glow_color = mobject.get_color()
    
    center_point = use_about_point if use_about_point is not None else mobject.get_center()
    
    # 从外到内创建辉光层
    for i in range(n_layers, 0, -1):
        glow_copy = mobject.copy()
        
        # 计算缩放比例
        current_scale = 1 + (scale_factor - 1) * (i / n_layers)
        glow_copy.scale(current_scale, about_point=center_point)
        
        # 计算透明度
        opacity = base_opacity * (1 - (i - 1) / n_layers) * 0.8 + base_opacity * 0.2
        
        # 应用样式
        glow_copy.set_stroke(color=glow_color, opacity=opacity)
        if glow_width is not None:
            glow_copy.set_stroke(width=glow_width)
        glow_copy.set_fill(color=glow_color, opacity=opacity * 0.5)
        
        glow_layers.add(glow_copy)
    
    return VGroup(glow_layers, mobject)


def create_glowing_arc_arrow(
    # 弧线参数
    start_angle=0,
    angle=TAU/2,
    radius=2.5,
    colors=None,
    stroke_width=4,
    # 辉光参数
    glow_color=None,
    n_glow_layers=8,
    arc_scale_factor=1.05,
    tip_scale_factor=1.5,
    glow_stroke_width=None,
    glow_width_mult=2.0,
    base_opacity=0.25,
    # 箭头参数
    add_tip=True,
    tip_at_start=False,
):
    """
    创建辉光弧形箭头 - 封装完整的辉光效果
    
    弧线参数:
        start_angle: 起始角度
        angle: 弧线角度
        radius: 半径
        colors: 颜色列表（渐变）
        stroke_width: 线条宽度（可以是列表实现变宽）
    
    辉光参数:
        glow_color: 辉光颜色，None则使用colors最后一个
        n_glow_layers: 辉光层数
        arc_scale_factor: 弧线辉光缩放倍数
        tip_scale_factor: 箭头尖端辉光缩放倍数
        glow_stroke_width: 辉光线条宽度，None则使用原始宽度的倍数
        glow_width_mult: 辉光宽度倍数
        base_opacity: 辉光透明度
    
    箭头参数:
        add_tip: 是否添加箭头尖端
        tip_at_start: 箭头尖端是否在起始位置
    
    返回:
        VGroup: 包含辉光层和原始箭头的组
    """
    if colors is None:
        colors = [WHITE]
    
    # 创建基础弧线
    arc = Arc(
        start_angle=start_angle,
        angle=angle,
        radius=radius
    )
    
    # 设置线条宽度
    arc.set_stroke(width=stroke_width)
    arc.set_color(colors)
    
    # 添加箭头尖端
    if add_tip:
        arc.add_tip(at_start=tip_at_start)
        arc.get_tips()[0].set_color(colors[-1])
    
    # 确定辉光颜色
    glow_col = glow_color if glow_color else colors[-1]
    
    # 计算辉光线条宽度
    if glow_stroke_width is None:
        if hasattr(stroke_width, '__iter__') and not isinstance(stroke_width, str):
            glow_width = [w * glow_width_mult for w in stroke_width]
        else:
            glow_width = stroke_width * glow_width_mult
    else:
        glow_width = glow_stroke_width
    
    # 获取箭头尖端（如果有）
    tips = arc.get_tips() if add_tip else []
    
    # 为弧线创建辉光层（移除箭头尖端）
    arc_glow_layers = VGroup()
    for i in range(n_glow_layers, 0, -1):
        arc_copy = arc.copy()
        
        # 移除箭头尖端
        if tips:
            for tip in arc_copy.get_tips():
                arc_copy.remove(tip)
        
        # 计算缩放和透明度
        current_scale = 1 + (arc_scale_factor - 1) * (i / n_glow_layers)
        opacity = base_opacity * (1 - (i - 1) / n_glow_layers) * 0.8 + base_opacity * 0.2
        
        # 以弧线中心为基准缩放
        arc_copy.scale(current_scale, about_point=arc_copy.get_center())
        arc_copy.set_stroke(color=glow_col, width=glow_width, opacity=opacity)
        
        arc_glow_layers.add(arc_copy)
    
    # 为箭头尖端创建辉光层
    tip_glow_layers = VGroup()
    if tips:
        for original_tip in tips:
            tip_center = original_tip.get_center()
            
            for i in range(n_glow_layers, 0, -1):
                tip_copy = original_tip.copy()
                
                current_scale = 1 + (tip_scale_factor - 1) * (i / n_glow_layers)
                opacity = base_opacity * (1 - (i - 1) / n_glow_layers) * 0.8 + base_opacity * 0.2
                
                tip_copy.scale(current_scale, about_point=tip_center)
                tip_copy.set_fill(color=glow_col, opacity=opacity)
                tip_copy.set_stroke(color=glow_col, opacity=opacity)
                
                tip_glow_layers.add(tip_copy)
    
    # 组合所有层并返回
    result = VGroup(arc_glow_layers, tip_glow_layers, arc)
    
    # 添加便捷属性访问
    result.arc = arc
    result.arc_glow = arc_glow_layers
    result.tip_glow = tip_glow_layers
    
    return result


# ========== 使用示例 ==========

class ChemicalCycleTapered(Scene):
    def construct(self):
        # 颜色配置
        LEFT_COLORS = ["#8B0000", "#FF4500", "#FFD700"]
        RIGHT_COLORS = ["#2C3E50", "#3498DB", "#E0FFFF"]
        TAPERED_WIDTH = [0, 4, 8, 12, 12, 12, 12, 12, 12, 12]
        TAPERED_WIDTH = [w/4 for w in TAPERED_WIDTH]

        # 创建辉光弧形箭头
        left_arrow = create_glowing_arc_arrow(
            start_angle=-TAU/4 - 0.6,
            angle=TAU/2,
            radius=2.5,
            colors=LEFT_COLORS,
            stroke_width=TAPERED_WIDTH,
            glow_color="#FFD700",
            n_glow_layers=8,
            arc_scale_factor=1.03,      # 弧线辉光缩放
            tip_scale_factor=1.5,       # 箭头辉光缩放
            glow_width_mult=2.5,        # 辉光宽度倍数
            base_opacity=0.3,
        )
        
        right_arrow = create_glowing_arc_arrow(
            start_angle=TAU/4 - 0.6,
            angle=TAU/2,
            radius=2.5,
            colors=RIGHT_COLORS,
            stroke_width=TAPERED_WIDTH,
            glow_color="#87CEEB",
            n_glow_layers=8,
            arc_scale_factor=1.03,
            tip_scale_factor=1.5,
            glow_width_mult=2.5,
            base_opacity=0.3,
        )
        
        # 错位布局
        left_arrow.shift(LEFT * 0.8)
        right_arrow.shift(RIGHT * 0.8)

        # 展示
        self.play(
            ShowCreation(left_arrow),
            ShowCreation(right_arrow),
            run_time=2
        )

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py")