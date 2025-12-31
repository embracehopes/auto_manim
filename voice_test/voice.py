"""
ManimGL 配音工作流演示
自动生成 AI 配音 + 动画同步

使用方法:
    python voice.py
"""

from manimlib import *
import os
import sys

# 添加 utils 到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, "utils"))

from tts_generator import TTSGenerator, generate_voice


class VoiceDemo(Scene):
    """
    完整配音工作流演示
    
    流程：
    1. 定义字幕列表
    2. 自动生成 AI 配音
    3. ManimGL 动画同步播放
    """
    
    def setup(self):
        super().setup()
        # 配置
        self.sounds_dir = os.path.join(project_root, "assets", "sounds")
        self.voice = "zh-CN-XiaoxiaoNeural"  # 可选：YunxiNeural（男声）
        
        # 字幕定义
        self.subtitles = [
            {"text": "欢迎观看本期视频", "duration": 2.5},
            {"text": "今天我们来学习勾股定理", "duration": 3.0},
            {"text": "在直角三角形中", "duration": 2.0},
            {"text": "两条直角边的平方和等于斜边的平方", "duration": 3.5},
            {"text": "感谢收看，下期再见", "duration": 2.5},
        ]
    
    def generate_all_voices(self):
        """预生成所有配音"""
        print("\n🎤 生成配音...")
        tts = TTSGenerator(voice=self.voice, rate="+5%")  # 稍微加快语速
        
        import asyncio
        
        async def gen_all():
            for i, sub in enumerate(self.subtitles):
                output_path = os.path.join(self.sounds_dir, f"subtitle_{i+1:03d}.mp3")
                await tts.generate(sub["text"], output_path)
                sub["audio"] = output_path
                print(f"  ✅ {i+1}/{len(self.subtitles)}: {sub['text'][:10]}...")
        
        asyncio.run(gen_all())
        print("✅ 配音生成完成！\n")
    
    def construct(self):
        # 先生成配音
        self.generate_all_voices()
        
        # 字幕对象
        current_sub = None
        
        for i, sub in enumerate(self.subtitles):
            # 创建字幕
            new_sub = Text(
                sub["text"],
                font="STKaiti",
                font_size=42,
                color=WHITE
            ).move_to(DOWN * 2.5)
            
            # 添加配音
            audio_path = sub.get("audio")
            if audio_path and os.path.exists(audio_path):
                self.add_sound(audio_path, time_offset=-0.1)
            
            # 动画
            if current_sub is None:
                self.play(Write(new_sub), run_time=0.5)
            else:
                self.play(
                    ReplacementTransform(current_sub, new_sub),
                    run_time=0.3
                )
            
            current_sub = new_sub
            
            # 等待配音播放完成
            wait_time = sub["duration"] - 0.5
            if wait_time > 0:
                self.wait(wait_time)
        
        # 结束
        self.play(FadeOut(current_sub), run_time=0.5)
        self.wait(0.5)


class QuickVoiceTest(Scene):
    """快速测试已生成的配音"""
    
    def construct(self):
        sounds_dir = os.path.join(project_root, "assets", "sounds")
        
        # 使用已生成的测试配音
        test_files = [
            ("line_001.mp3", "欢迎观看本期视频"),
            ("line_002.mp3", "今天我们来学习勾股定理"),
            ("line_003.mp3", "感谢收看，下期再见"),
        ]
        
        current_text = None
        
        for filename, text in test_files:
            audio_path = os.path.join(sounds_dir, filename)
            
            new_text = Text(
                text,
                font="STKaiti",
                font_size=48
            ).move_to(DOWN * 2)
            
            # 添加配音
            if os.path.exists(audio_path):
                self.add_sound(audio_path, time_offset=0)
                print(f"🔊 播放: {filename}")
            
            # 动画
            if current_text is None:
                self.play(Write(new_text), run_time=0.5)
            else:
                self.play(
                    ReplacementTransform(current_text, new_text),
                    run_time=0.3
                )
            
            current_text = new_text
            self.wait(2.0)
        
        self.play(FadeOut(current_text), run_time=0.5)


if __name__ == "__main__":
    script_name = os.path.basename(__file__).replace(".py", "")
    # 运行 QuickVoiceTest（使用已生成的配音）
    os.system(f'cd "{script_dir}" && manimgl {script_name}.py QuickVoiceTest -w')