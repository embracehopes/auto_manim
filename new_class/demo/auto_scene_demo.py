"""
AutoScene 基础功能演示

演示内容：
- 时间轴字幕同步
- 自动配音生成
- 调试 HUD

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl auto_scene_demo.py AutoSceneDemo -w
"""

import os
import sys

# 添加父目录到路径以导入 AutoScene
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auto_scene import AutoScene
from manimlib import YELLOW, RED, GREEN


class AutoSceneDemo(AutoScene):
    """AutoScene 功能演示"""
    
    def construct(self):
        # 启用调试
        self.enable_debug(True)
        self.enable_time_hud()
        
        # 设置字幕样式（可选）
        self.set_subtitle_style(font_size=28, edge_buff=0.3)
        
        # 定义时间轴（支持着色）
        timeline = [
            {"start": 0.0, "end": 2.5, "text": "欢迎观看本教程"},
            {"start": 2.5, "end": 5.0, "text": "这是自动化字幕演示", 
             "color_map": {"自动化": YELLOW, "字幕": RED}},
            {"start": 5.0, "end": 7.5, "text": "配音已自动生成",
             "color_map": {"配音": GREEN}},
        ]
        
        # 验证时间轴
        print("\n🔍 验证时间轴...")
        self.validate_timeline(timeline)
        
        # 运行时间轴
        print("\n🎬 运行时间轴...")
        self.run_timeline(timeline)
        
        # 显示标记
        print(f"\n📍 标记: {self.get_markers()}")
        print(f"⏱️ 最终时间: {self.get_current_time():.2f}s")


if __name__ == "__main__":
    os.system(f"cd {script_dir} && manimgl auto_scene_demo.py AutoSceneDemo")
