from manimlib import *
from colour import Color



class manim(ThreeDScene):
    def construct(self):

        sphere = Sphere(radius=2)  
        sphere.set_color(Color(rgb=(1.0, 0, 0)))
        lambert_code = """  
        vec3 light_dir = normalize(light_position - point);  
        float lambert = max(dot(unit_normal, light_dir), 0.0);

        //I want to define a custom parameter
        color.rgb = vec3(lambert) /* * custom_parameter */;
        """
        sphere.replace_shader_code(  
            "///// INSERT COLOR FUNCTION HERE /////",  
            lambert_code  
        )
        self.add(sphere)

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")