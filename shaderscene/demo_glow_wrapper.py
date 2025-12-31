from manimlib import *
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from mobject.glow_wrapper import GlowWrapperEffect


class GlowWrapperDemo(Scene):
    def construct(self):
        title = Text("GlowWrapperEffect", font="STKaiti", font_size=48)
        glow_title = GlowWrapperEffect(
            title,
            curve_sample_factor=32,
            min_curve_samples=480,
            glow_width=0.12,
            glow_factor=3.8,
            color_scheme="neon",
        )
        self.play(Write(title))
        self.play(FadeIn(glow_title))
        self.wait(1.5)

        group = VGroup()
        shapes = []
        labels = []

        square = Square(side_length=2.5, color=BLUE, fill_opacity=0.2).shift(LEFT * 4)
        circle = Circle(radius=1.5, color=GREEN, fill_opacity=0.2)
        star = RegularPolygon(7, color=YELLOW, fill_opacity=0.15).shift(RIGHT * 4)

        shapes.extend([square, circle, star])

        for shape in shapes:
            label = Text(shape.__class__.__name__, font_size=26)
            label.next_to(shape, DOWN, buff=0.4)
            labels.append(label)

        glows = [
            GlowWrapperEffect(
                square,
                color_scheme=["#00D2FF", "#0066FF"],
                glow_width=0.38,
                curve_sample_factor=24,
                min_curve_samples=360,
            ),
            GlowWrapperEffect(
                circle,
                color_scheme="single",
                single_color="#00FFC6",
                glow_width=0.45,
                glow_factor=4.0,
                curve_sample_factor=48,
                min_curve_samples=540,
            ),
            GlowWrapperEffect(
                star,
                color_scheme=["#FFB347", "#FF005C"],
                glow_width=0.35,
                curve_sample_factor=36,
                min_curve_samples=420,
            ),
        ]

        self.play(*[FadeIn(mob) for mob in shapes])
        self.play(*[FadeIn(gl) for gl in glows])
        self.play(*[Write(label) for label in labels])
        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(0.5)


class GlowWrapperStyleDemo(Scene):
    def construct(self):
        base = VGroup(
            
            RegularPolygon(5, color=PURPLE_C, fill_opacity=0.15).scale(1.6),
        ).arrange(DOWN, buff=1.0)
        base =Text("Glow Style Controller", font_size=40)

        self.play(FadeIn(base))

        glow = GlowWrapperEffect(
            base,
            color=GREEN,
            size=0.05
         

        )

        self.play(FadeIn(glow))



if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py GlowWrapperStyleDemo ")