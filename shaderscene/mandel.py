from manimlib import *
import os


class ShaderMobject(Mobject):
    """自定义Shader Mobject基类，用于加载和使用自定义shader"""
    
    def __init__(
        self,
        shader_folder: str,
        data_dtype: np.dtype = [("point", np.float32, (3,))],
        height: float = FRAME_HEIGHT,
        aspect_ratio: float = 16 / 9,
        **kwargs,
    ):
        self.aspect_ratio = aspect_ratio
        self.shader_folder = shader_folder
        self.data_dtype = data_dtype

        super().__init__(**kwargs)
        self.set_height(height, stretch=True)
        self.set_width(height * aspect_ratio, stretch=True)

    def init_data(self, length: int = 4) -> None:
        super().init_data(length=length)
        self.data["point"][:] = [UL, DL, UR, DR]

    def set_color(self, *args, **kwargs):
        return self


class MandelbrotShader(ShaderMobject):
    """基于Shader的Mandelbrot分形"""
    
    # Shader 文件夹路径（相对于当前文件）
    shader_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "shaderscene", "mandelbrot_shader"
    )
    
    # 经典Mandelbrot调色盘
    colors = [
        "#000764",  # color0 - 深蓝
        "#206BCB",  # color1 - 蓝色
        "#EDFFFF",  # color2 - 浅蓝白
        "#FFAA00",  # color3 - 橙色
        "#000200",  # color4 - 黑色
        "#000764",  # color5 - 深蓝
        "#206BCB",  # color6 - 蓝色  
        "#EDFFFF",  # color7 - 浅蓝白
        "#FFAA00",  # color8 - 橙色
    ]
    
    def __init__(
        self,
        n_steps: float = 100.0,
        scale_factor: float = 3.5,
        offset: np.ndarray = None,
        parameter: np.ndarray = None,
        is_mandelbrot: bool = True,
        opacity: float = 1.0,
        colors: list = None,
        **kwargs,
    ):
        self.n_steps = n_steps
        self.scale_factor = scale_factor
        self.offset = offset if offset is not None else np.array([-0.5, 0.0, 0.0])
        self.parameter = parameter if parameter is not None else np.array([0.0, 0.0])
        self.is_mandelbrot = is_mandelbrot
        self._opacity = opacity
        if colors is not None:
            self.colors = colors
            
        super().__init__(
            shader_folder=self.shader_folder,
            **kwargs
        )
    
    def init_uniforms(self):
        super().init_uniforms()
        
        # 设置基本uniforms
        self.uniforms["n_steps"] = float(self.n_steps)
        self.uniforms["scale_factor"] = float(self.scale_factor)
        self.uniforms["offset"] = np.array(self.offset, dtype=np.float32)
        self.uniforms["parameter"] = np.array(self.parameter, dtype=np.float32)
        self.uniforms["mandelbrot"] = 1.0 if self.is_mandelbrot else 0.0
        self.uniforms["opacity"] = float(self._opacity)
        
        # 设置颜色uniforms
        for i, color in enumerate(self.colors):
            rgba = color_to_rgba(color)
            self.uniforms[f"color{i}"] = np.array(rgba[:3], dtype=np.float32)
    
    def set_n_steps(self, n_steps: float):
        """设置迭代次数"""
        self.n_steps = n_steps
        self.uniforms["n_steps"] = float(n_steps)
        return self
    
    def set_scale(self, scale_factor: float):
        """设置缩放因子"""
        self.scale_factor = scale_factor
        self.uniforms["scale_factor"] = float(scale_factor)
        return self
    
    def set_offset(self, offset: np.ndarray):
        """设置偏移量（复平面中心）"""
        self.offset = offset
        self.uniforms["offset"] = np.array(offset, dtype=np.float32)
        return self
    
    def set_parameter(self, parameter: np.ndarray):
        """设置Julia集参数"""
        self.parameter = parameter
        self.uniforms["parameter"] = np.array(parameter, dtype=np.float32)
        return self


class MandelbrotPrecisionScene(Scene):
    """精度随时间增加的Mandelbrot分形场景（基于Shader）"""
    
    def construct(self):
        plane=NumberPlane()
        self.add(plane)
        fractal = MandelbrotShader(
            n_steps=5,
            scale_factor=3.5,
            offset=np.array([-0.5, 0.0, 0.0]),
            opacity=0.5
        )
        self.add(fractal)
        
        # 标题
        title = Tex("Mandelbrot Set", font_size=48)
        title.to_edge(UP)
        title.set_backstroke(BLACK, 3)
        self.add(title)
        
        # 迭代次数显示
        iter_label = VGroup(
            Tex("迭代次数: ", font_size=32),
            Integer(5, font_size=32)
        ).arrange(RIGHT)
        iter_label.to_corner(UR)
        iter_label.set_backstroke(BLACK, 3)
        self.add(iter_label)
        
        # 迭代次数序列
        iterations_sequence = [5, 10, 20, 35, 50, 75, 100, 150, 200, 300, 500, 1000]
        
        self.wait(0.5)
        
        # 逐步增加精度
        for n_steps in iterations_sequence[1:]:
            # 更新迭代次数
            fractal.set_n_steps(n_steps)
            iter_label[1].set_value(n_steps)
            
            # 等待时间随迭代次数调整
            if n_steps >= 500:
                self.wait(1.0)
            elif n_steps >= 200:
                self.wait(0.5)
            else:
                self.wait(0.3)
        
        self.wait(2)


class MandelbrotZoomScene(InteractiveScene):
    """可交互的Mandelbrot分形缩放场景"""
    
    def construct(self):
        # 创建高精度Mandelbrot分形
        fractal = MandelbrotShader(
            n_steps=200,
            scale_factor=3.5,
            offset=np.array([-0.5, 0.0, 0.0]),
        )
        self.add(fractal)
        
        # 标题
        title = Text("Mandelbrot Set - Interactive", font_size=36)
        title.to_edge(UP)
        title.set_backstroke(BLACK, 3)
        self.add(title)
        
        # 显示缩放信息
        info_label = VGroup(
            Text("Scale: ", font_size=24),
            DecimalNumber(3.5, num_decimal_places=4, font_size=24),
        ).arrange(RIGHT)
        info_label.to_corner(DR)
        info_label.set_backstroke(BLACK, 2)
        self.add(info_label)
        
        self.wait()
        
        # 缩放动画：放大到经典的"海马谷"区域
        target_offset = np.array([-0.745, 0.186, 0.0])
        target_scale = 0.01
        
        # 使用ValueTracker控制动画
        scale_tracker = ValueTracker(3.5)
        offset_x_tracker = ValueTracker(-0.5)
        offset_y_tracker = ValueTracker(0.0)
        
        def update_fractal(m):
            m.set_scale(scale_tracker.get_value())
            m.set_offset(np.array([
                offset_x_tracker.get_value(),
                offset_y_tracker.get_value(),
                0.0
            ]))
            # 动态增加迭代次数以保持细节
            scale = scale_tracker.get_value()
            n_steps = int(100 + 200 * np.log10(3.5 / max(scale, 0.0001)))
            m.set_n_steps(min(n_steps, 2000))
        
        fractal.add_updater(update_fractal)
        info_label[1].add_updater(lambda d: d.set_value(scale_tracker.get_value()))
        
        # 执行缩放动画
        self.play(
            scale_tracker.animate.set_value(target_scale),
            offset_x_tracker.animate.set_value(target_offset[0]),
            offset_y_tracker.animate.set_value(target_offset[1]),
            run_time=8,
            rate_func=smooth,
        )
        
        fractal.remove_updater(update_fractal)
        self.wait(2)
        
        # 进入交互模式
        self.embed()


class JuliaSetScene(Scene):
    """Julia集场景 - 参数沿心形边界移动"""
    
    def construct(self):
        # 创建Julia集分形
        fractal = MandelbrotShader(
            n_steps=200,
            scale_factor=3.0,
            offset=np.array([0.0, 0.0, 0.0]),
            is_mandelbrot=False,
            parameter=np.array([0.0, 0.0]),
        )
        self.add(fractal)
        
        # 标题
        title = Text("Julia Set", font_size=48)
        title.to_edge(UP)
        title.set_backstroke(BLACK, 3)
        self.add(title)
        
        # 参数显示
        c_label = VGroup(
            Text("c = ", font_size=28),
            DecimalNumber(0, num_decimal_places=3, font_size=28),
            Text(" + ", font_size=28),
            DecimalNumber(0, num_decimal_places=3, font_size=28),
            Text("i", font_size=28),
        ).arrange(RIGHT, buff=0.1)
        c_label.to_corner(UR)
        c_label.set_backstroke(BLACK, 2)
        self.add(c_label)
        
        # 心形边界参数方程
        def cardioid_point(t):
            z = np.exp(1j * t) / 2 - np.exp(2j * t) / 4
            return z.real, z.imag
        
        # 动画控制器
        tracker = ValueTracker(0)
        
        def update_fractal(m):
            t = tracker.get_value()
            cx, cy = cardioid_point(t)
            m.set_parameter(np.array([cx, cy]))
        
        fractal.add_updater(update_fractal)
        c_label[1].add_updater(lambda d: d.set_value(cardioid_point(tracker.get_value())[0]))
        c_label[3].add_updater(lambda d: d.set_value(cardioid_point(tracker.get_value())[1]))
        
        # 沿心形边界移动
        self.play(
            tracker.animate.set_value(TAU),
            run_time=15,
            rate_func=linear,
        )
        
        self.wait()


class MandelbrotFractal(Mobject):
    """Mandelbrot分形 - 使用manimlib内置的mandelbrot_fractal shader"""
    
    shader_folder = "mandelbrot_fractal"
    
    # 颜色映射（9种颜色）
    CONFIG = {
        "colors": [
            "#000764",  # color0 - 深蓝
            "#206BCB",  # color1 - 蓝色
            "#EDFFFF",  # color2 - 浅蓝白
            "#FFAA00",  # color3 - 橙色
            "#000200",  # color4 - 黑色
            "#000764",  # color5 - 深蓝
            "#206BCB",  # color6 - 蓝色  
            "#EDFFFF",  # color7 - 浅蓝白
            "#FFAA00",  # color8 - 橙色
        ],
        "n_steps": 100,      # 迭代次数
        "parameter": [0, 0], # Julia集参数（mandelbrot模式时无效）
        "mandelbrot": 1.0,   # 1.0=Mandelbrot集, 0.0=Julia集
        "opacity": 1.0,
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 创建一个覆盖整个屏幕的矩形
        self.rect = FullScreenRectangle()
        self.add(self.rect)
    
    def init_uniforms(self):
        super().init_uniforms()
        self.uniforms.update({
            "n_steps": float(self.CONFIG["n_steps"]),
            "parameter": np.array(self.CONFIG["parameter"], dtype=np.float32),
            "mandelbrot": float(self.CONFIG["mandelbrot"]),
            "opacity": float(self.CONFIG["opacity"]),
        })
        # 设置颜色uniforms
        for i, color in enumerate(self.CONFIG["colors"]):
            rgba = color_to_rgba(color)
            self.uniforms[f"color{i}"] = np.array(rgba[:3], dtype=np.float32)


class MandelbrotScene(Scene):
    """展示Mandelbrot分形的场景"""
    
    def construct(self):
        # 方法1：直接使用FullScreenRectangle + shader
        plane = FullScreenRectangle()
        plane.set_color_by_code("""
            vec3 c = vec3(0.0);
            frag_color = vec4(c, 1.0);
        """)
        
        # 设置shader相关uniforms
        plane.uniforms["n_steps"] = 100.0
        plane.uniforms["parameter"] = np.array([0.0, 0.0], dtype=np.float32)
        plane.uniforms["mandelbrot"] = 1.0
        plane.uniforms["opacity"] = 1.0
        
        # 设置颜色映射
        colors = [
            "#000764", "#206BCB", "#EDFFFF", "#FFAA00", "#000200",
            "#000764", "#206BCB", "#EDFFFF", "#FFAA00"
        ]
        for i, color in enumerate(colors):
            rgba = color_to_rgba(color)
            plane.uniforms[f"color{i}"] = np.array(rgba[:3], dtype=np.float32)
        
        self.add(plane)
        self.wait()


class MandelbrotZoom(InteractiveScene):
    """可交互的Mandelbrot分形缩放"""
    
    def construct(self):
        # 使用NumberPlane作为背景坐标系
        plane = ComplexPlane(
            x_range=[-3, 2, 1],
            y_range=[-1.5, 1.5, 1],
            background_line_style={
                "stroke_opacity": 0.3,
            }
        )
        plane.add_coordinates()
        
        # 创建分形显示
        # 由于manimgl的shader系统，我们需要自定义渲染
        self.add(plane)
        
        # 添加说明文字
        title = Text("Mandelbrot Set", font_size=48)
        title.to_corner(UL)
        self.add(title)
        
        # 标记一些有趣的点
        interesting_points = [
            (-0.75, 0),      # 主心形边界
            (-1.25, 0),      # 周期2泡泡
            (-0.1, 0.65),    # 螺旋区域
            (0.28, 0.53),    # 小Mandelbrot副本
        ]
        
        dots = VGroup()
        for x, y in interesting_points:
            dot = Dot(plane.c2p(x, y), color=YELLOW, radius=0.08)
            dots.add(dot)
        
        self.add(dots)
        self.wait()
        self.embed()


class JuliaSetAnimation(Scene):
    """Julia集动画 - 参数c沿Mandelbrot边界移动"""
    
    def construct(self):
        # 创建坐标平面
        plane = ComplexPlane(
            x_range=[-2, 2, 0.5],
            y_range=[-2, 2, 0.5],
        )
        
        # 标题
        title = Text("Julia Set", font_size=36)
        title.to_corner(UL)
        
        # 参数c的显示
        c_label = VGroup(
            Text("c = ", font_size=24),
            DecimalNumber(0, num_decimal_places=3, font_size=24),
            Text(" + ", font_size=24),
            DecimalNumber(0, num_decimal_places=3, font_size=24),
            Text("i", font_size=24),
        ).arrange(RIGHT, buff=0.1)
        c_label.to_corner(UR)
        
        self.add(plane, title, c_label)
        
        # 在主心形边界上选取参数
        # 主心形的参数方程：c = (e^(it)/2) - (e^(2it)/4)
        def cardioid_point(t):
            z = np.exp(1j * t) / 2 - np.exp(2j * t) / 4
            return z.real, z.imag
        
        # 动画：沿心形边界移动
        tracker = ValueTracker(0)
        
        # 标记当前c点
        c_dot = Dot(color=RED, radius=0.1)
        c_dot.add_updater(lambda d: d.move_to(
            plane.c2p(*cardioid_point(tracker.get_value()))
        ))
        
        self.add(c_dot)
        
        # 更新参数显示
        c_label[1].add_updater(lambda d: d.set_value(cardioid_point(tracker.get_value())[0]))
        c_label[3].add_updater(lambda d: d.set_value(cardioid_point(tracker.get_value())[1]))
        
        self.play(tracker.animate.set_value(TAU), run_time=10, rate_func=linear)
        self.wait()


class SimpleMandelbrot(Scene):
    """简单的Mandelbrot分形显示 - 精度随时间增加"""
    
    def construct(self):
        from PIL import Image
        
        width, height = 800, 600
        x_min, x_max = -2.5, 1.0
        y_min, y_max = -1.25, 1.25
        
        # 创建复数网格（只需计算一次）
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        def compute_mandelbrot(max_iter):
            """计算Mandelbrot集，返回逃逸时间矩阵"""
            Z = np.zeros_like(C)
            M = np.zeros(C.shape)
            
            for i in range(max_iter):
                mask = np.abs(Z) <= 2
                Z[mask] = Z[mask] ** 2 + C[mask]
                M[mask] = i
            
            return M, max_iter
        
        def colorize(M, max_iter):
            """将逃逸时间转换为彩色图像"""
            # 归一化
            M_norm = M / max_iter
            
            img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 使用更丰富的颜色映射
            for i in range(height):
                for j in range(width):
                    t = M_norm[i, j]
                    if M[i, j] >= max_iter - 1:
                        # 集合内部 - 黑色
                        img[i, j] = [0, 0, 0]
                    else:
                        # 外部 - 使用周期性颜色映射
                        # 使用对数平滑
                        hue = (t * 10) % 1.0
                        
                        # HSV到RGB的简化转换
                        if hue < 1/6:
                            r, g, b = 255, int(255 * hue * 6), 0
                        elif hue < 2/6:
                            r, g, b = int(255 * (2 - hue * 6)), 255, 0
                        elif hue < 3/6:
                            r, g, b = 0, 255, int(255 * (hue * 6 - 2))
                        elif hue < 4/6:
                            r, g, b = 0, int(255 * (4 - hue * 6)), 255
                        elif hue < 5/6:
                            r, g, b = int(255 * (hue * 6 - 4)), 0, 255
                        else:
                            r, g, b = 255, 0, int(255 * (6 - hue * 6))
                        
                        img[i, j] = [r, g, b]
            
            return img
        
        # 迭代次数序列：从低到高
        iterations_sequence = [5, 10, 20, 35, 50, 75, 100, 150, 200, 300, 500, 5000]
        
        # 标题
        title = Text("Mandelbrot Set", font_size=48)
        title.to_edge(UP)
        title.set_backstroke(BLACK, 3)
        self.add(title)
        
        # 迭代次数显示
        iter_label = VGroup(
            Text("迭代次数: ", font_size=32),
            Integer(0, font_size=32)
        ).arrange(RIGHT)
        iter_label.to_corner(UR)
        iter_label.set_backstroke(BLACK, 3)
        self.add(iter_label)
        
        # 当前显示的图像
        current_image = None
        
        for idx, max_iter in enumerate(iterations_sequence):
            # 计算分形
            M, _ = compute_mandelbrot(max_iter)
            img = colorize(M, max_iter)
            
            # 保存为临时图片
            pil_img = Image.fromarray(img)
            temp_path = f"mandelbrot_temp_{idx}.png"
            pil_img.save(temp_path)
            
            # 创建ImageMobject
            new_image = ImageMobject(temp_path)
            new_image.set_height(FRAME_HEIGHT)
            
            # 更新迭代次数显示
            iter_label[1].set_value(max_iter)
            
            if current_image is None:
                # 第一帧直接添加
                self.add(new_image)
                current_image = new_image
                self.wait(0.5)
            else:
                # 淡入淡出切换
                self.play(
                    FadeOut(current_image),
                    FadeIn(new_image),
                    run_time=0.3
                )
                self.remove(current_image)
                current_image = new_image
                
                # 高迭代时停留更长
                if max_iter >= 200:
                    self.wait(1.0)
                elif max_iter >= 100:
                    self.wait(0.5)
                else:
                    self.wait(0.3)
        
        # 最终效果停留
        self.wait(2)
        
        # 清理临时文件
        import os
        for idx in range(len(iterations_sequence)):
            try:
                os.remove(f"mandelbrot_temp_{idx}.png")
            except:
                pass


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本，选择要运行的场景
    # 可选场景：
    #   - MandelbrotPrecisionScene: 精度随时间增加（推荐）
    #   - MandelbrotZoomScene: 可交互缩放
    #   - JuliaSetScene: Julia集动画
    #   - SimpleMandelbrot: 基于numpy的版本（备用）
    os.system(f"cd {script_dir} && manimgl {script_name}.py JuliaSetScene ")