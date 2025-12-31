from manimlib import *
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from my_dash_mobject import *

class glowflashrectangle(Scene):
    def construct(self):

        a = ValueTracker(0)
        r = Rectangle(width=3,height=2)
        dr = always_redraw(lambda:
            MyDashMobject(r, dash_offset=a.get_value()%1)
        )
        rate_func=lambda t, start_t=start_t: (t + start_t) % 1
        self.add(dr)
        self.play(a.animate.set_value(3),run_time=5,rate_func=lambda t: smooth(smooth(t)))
if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")

        
