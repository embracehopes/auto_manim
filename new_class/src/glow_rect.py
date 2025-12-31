from manimlib import *

# ========== 辉光矩形框 API ==========

def create_glow_surrounding_rect(
    mobject,
    # 矩形参数
    color=YELLOW,
    buff=0.15,
    stroke_width=3,
    fill_opacity=0,
    # 辉光参数
    glow_color=None,
    n_glow_layers=3,          # 辉光层数（2-3层即可）
    max_glow_width=20,        # 最外层辉光宽度
    base_opacity=0.15,        # 最外层透明度
):
    """
    创建带辉光效果的环绕矩形 - 通过宽度和透明度渐变实现
    
    矩形参数:
        mobject: 要环绕的对象
        color: 矩形颜色
        buff: 矩形与对象的间距
        stroke_width: 线条宽度
        fill_opacity: 填充透明度
    
    辉光参数:
        glow_color: 辉光颜色，None则使用color
        n_glow_layers: 辉光层数（2-3层即可）
        max_glow_width: 最外层辉光线条宽度
        base_opacity: 最外层透明度
    
    返回:
        VGroup: 包含辉光层和原始矩形的组
    """
    # 创建基础矩形
    rect = SurroundingRectangle(
        mobject,
        color=color,
        buff=buff,
        stroke_width=stroke_width,
    )
    rect.set_fill(color=color, opacity=fill_opacity)
    
    # 确定辉光颜色
    glow_col = glow_color if glow_color else color
    
    # 创建辉光层（从外到内，宽度递减，透明度递增）
    glow_layers = VGroup()
    
    for i in range(n_glow_layers, 0, -1):
        glow_copy = rect.copy()
        
        # 宽度从 max_glow_width 渐变到 stroke_width
        ratio = i / n_glow_layers
        glow_width = stroke_width + (max_glow_width - stroke_width) * ratio
        
        # 透明度从 base_opacity 渐变到更高
        opacity = base_opacity + (0.5 - base_opacity) * (1 - ratio)
        
        glow_copy.set_stroke(color=glow_col, width=glow_width, opacity=opacity)
        glow_copy.set_fill(opacity=0)
        
        glow_layers.add(glow_copy)
    
    # 组合并返回
    result = VGroup(glow_layers, rect)
    result.rect = rect
    result.glow_layers = glow_layers
    
    return result


def create_glow_rect(
    width=4,
    height=2,
    # 矩形参数
    color=BLUE,
    corner_radius=0.1,
    stroke_width=3,
    fill_color=None,
    fill_opacity=0,
    # 辉光参数
    glow_color=None,
    n_glow_layers=3,
    max_glow_width=20,
    base_opacity=0.15,
):
    """
    创建带辉光效果的矩形 - 通过宽度和透明度渐变实现
    
    矩形参数:
        width: 矩形宽度
        height: 矩形高度
        color: 矩形边框颜色
        corner_radius: 圆角半径
        stroke_width: 线条宽度
        fill_color: 填充颜色
        fill_opacity: 填充透明度
    
    辉光参数:
        glow_color: 辉光颜色，None则使用color
        n_glow_layers: 辉光层数（2-3层即可）
        max_glow_width: 最外层辉光宽度
        base_opacity: 最外层透明度
    
    返回:
        VGroup: 包含辉光层和原始矩形的组
    """
    # 创建基础矩形
    if corner_radius > 0:
        rect = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=corner_radius,
            stroke_color=color,
            stroke_width=stroke_width,
        )
    else:
        rect = Rectangle(
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=stroke_width,
        )
    
    fill_col = fill_color if fill_color else color
    rect.set_fill(color=fill_col, opacity=fill_opacity)
    
    # 确定辉光颜色
    glow_col = glow_color if glow_color else color
    
    # 创建辉光层（从外到内，宽度递减，透明度递增）
    glow_layers = VGroup()
    
    for i in range(n_glow_layers, 0, -1):
        glow_copy = rect.copy()
        
        # 宽度从 max_glow_width 渐变到 stroke_width
        ratio = i / n_glow_layers
        glow_width = stroke_width + (max_glow_width - stroke_width) * ratio
        
        # 透明度从 base_opacity 渐变到更高
        opacity = base_opacity + (0.5 - base_opacity) * (1 - ratio)
        
        glow_copy.set_stroke(color=glow_col, width=glow_width, opacity=opacity)
        glow_copy.set_fill(opacity=0)
        
        glow_layers.add(glow_copy)
    
    # 组合并返回
    result = VGroup(glow_layers, rect)
    result.rect = rect
    result.glow_layers = glow_layers
    
    return result


# ========== 使用示例 ==========

class GlowRectDemo(Scene):
    def construct(self):
        # 创建一些文本对象
        title = Text("辉光矩形框效果", font="STKaiti", font_size=48)
        title.to_edge(UP)
        
        formula = Tex(r"E = mc^2", font_size=72)
        
        # 创建辉光环绕矩形
        glow_box = create_glow_surrounding_rect(
            formula,
            color=YELLOW,
            buff=0.3,
            stroke_width=4,
            glow_color="#FFD700",
            n_glow_layers=3,
            max_glow_width=25,
            base_opacity=0.15,
        )
        
        # 创建独立的辉光矩形
        glow_rect1 = create_glow_rect(
            width=3,
            height=1.5,
            color=BLUE,
            corner_radius=0.15,
            stroke_width=3,
            glow_color="#87CEEB",
            n_glow_layers=3,
            max_glow_width=20,
            base_opacity=0.15,
        )
        glow_rect1.shift(DOWN * 2 + LEFT * 3)
        
        glow_rect2 = create_glow_rect(
            width=3,
            height=1.5,
            color=RED,
            corner_radius=0.15,
            stroke_width=3,
            glow_color="#FF6B6B",
            n_glow_layers=3,
            max_glow_width=20,
            base_opacity=0.15,
        )
        glow_rect2.shift(DOWN * 2 + RIGHT * 3)
        
        # 动画展示
        self.play(Write(title))
        self.play(Write(formula))
        self.play(ShowCreation(glow_box), run_time=1.5)
        self.wait(0.5)
        self.play(
            ShowCreation(glow_rect1),
            ShowCreation(glow_rect2),
            run_time=1.5
        )
        self.wait()


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py")
