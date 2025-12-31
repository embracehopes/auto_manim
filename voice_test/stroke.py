from manimlib import *

class linestroke(Scene):
    def construct(self):
        line = Line(LEFT*4, RIGHT*4)
        line.set_stroke(color=[WHITE, YELLOW], width=[0.2,5],opacity=[0.2,1])    
        self.add(line)
        self.wait(2)
        self.play(line.animate.set_stroke(width=10),run_time=2)
        self.wait(2)
        gloss = Gloss(line)
        self.play(ShowCreation(gloss))
        self.wait(2)
    
if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")