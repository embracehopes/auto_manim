"""
AutoScene 演示集合

包含多个演示场景，展示 AutoScene 的各种功能：

- auto_scene_demo.py: 基础功能演示（时间轴、字幕、配音）
- enhancement_demo.py: 增强功能演示（高亮、标注、相机聚焦）
- curved_annotation_demo.py: 弯曲箭头标注演示
- focus_guide_demo.py: 方框引导高亮演示
- tex_matching_demo.py: Tex 公式字符串匹配演示
- camera_focus_guide_demo.py: 带相机移动的方框引导演示

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl <文件名>.py <场景类名> -w
"""

from .auto_scene_demo import AutoSceneDemo
from .enhancement_demo import AutoSceneEnhancementDemo
from .curved_annotation_demo import CurvedAnnotationDemo
from .focus_guide_demo import FocusGuideDemo
from .tex_matching_demo import TexMatchingDemo
from .camera_focus_guide_demo import CameraFocusGuideDemo

__all__ = [
    'AutoSceneDemo',
    'AutoSceneEnhancementDemo', 
    'CurvedAnnotationDemo',
    'FocusGuideDemo',
    'TexMatchingDemo',
    'CameraFocusGuideDemo',
]

