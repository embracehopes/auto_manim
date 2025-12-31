"""
展示 edge-tts 所有中文音色的 ManimGL 动画
每种音色播放一句示例
"""

from manimlib import *
import os
import sys
import asyncio

# 添加 utils 到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, "utils"))

from tts_generator import TTSGenerator


def generate_all_voice_samples():
    """预生成所有中文语音样本"""
    print("\n🎤 获取所有中文语音...")
    
    # 获取所有中文语音
    voices = TTSGenerator.list_voices_sync("zh-CN")
    
    sounds_dir = os.path.join(project_root, "assets", "sounds", "voice_demo")
    os.makedirs(sounds_dir, exist_ok=True)
    
    test_text = "你好，我是人工智能配音"
    
    voice_data = []
    
    for voice in voices:
        short_name = voice["ShortName"]
        gender = voice["Gender"]
        
        # 生成文件名
        safe_name = short_name.replace("-", "_")
        output_path = os.path.join(sounds_dir, f"{safe_name}.mp3")
        
        # 如果文件不存在则生成
        if not os.path.exists(output_path):
            print(f"  生成: {short_name} ({gender})...")
            tts = TTSGenerator(voice=short_name)
            asyncio.run(tts.generate(test_text, output_path))
        else:
            print(f"  跳过: {short_name} (已存在)")
        
        voice_data.append({
            "name": short_name,
            "gender": gender,
            "audio": output_path,
            "display": short_name.replace("zh-CN-", "").replace("Neural", "")
        })
    
    print(f"\n✅ 共 {len(voice_data)} 种中文语音\n")
    return voice_data


class VoiceShowcase(Scene):
    """
    展示所有中文音色
    每种音色播放示例音频
    """
    
    def construct(self):
        # 预生成所有语音样本
        voice_data = generate_all_voice_samples()
        
        # 标题
        title = Text(
            "Edge-TTS 中文语音展示",
            font="STKaiti",
            font_size=56,
            color=YELLOW
        ).to_edge(UP, buff=0.5)
        
        underline = Line(
            title.get_left() + DOWN * 0.2,
            title.get_right() + DOWN * 0.2,
            color=YELLOW,
            stroke_width=3
        )
        
        self.play(Write(title), GrowFromCenter(underline), run_time=1.0)
        self.wait(0.5)
        
        # 示例文本显示
        sample_text = Text(
            '"你好，我是人工智能配音"',
            font="STKaiti",
            font_size=32,
            color=GREY_B
        ).next_to(underline, DOWN, buff=0.3)
        
        self.play(FadeIn(sample_text), run_time=0.5)
        
        # 当前语音显示区域
        voice_display = VGroup()
        
        current_voice_name = None
        current_voice_info = None
        
        for i, voice in enumerate(voice_data):
            # 语音名称
            gender_color = PINK if voice["gender"] == "Female" else BLUE
            gender_text = "♀ 女声" if voice["gender"] == "Female" else "♂ 男声"
            
            new_voice_name = Text(
                voice["display"],
                font="Arial",
                font_size=72,
                color=WHITE
            ).move_to(ORIGIN)
            
            new_voice_info = Text(
                gender_text,
                font="STKaiti",
                font_size=36,
                color=gender_color
            ).next_to(new_voice_name, DOWN, buff=0.3)
            
            # 序号
            counter = Text(
                f"{i+1}/{len(voice_data)}",
                font="Arial",
                font_size=28,
                color=GREY
            ).to_corner(DR, buff=0.5)
            
            # 播放音频
            if os.path.exists(voice["audio"]):
                self.add_sound(voice["audio"], time_offset=0)
            
            # 动画
            if current_voice_name is None:
                self.play(
                    Write(new_voice_name),
                    FadeIn(new_voice_info),
                    FadeIn(counter),
                    run_time=0.5
                )
            else:
                self.play(
                    ReplacementTransform(current_voice_name, new_voice_name),
                    ReplacementTransform(current_voice_info, new_voice_info),
                    ReplacementTransform(self.counter, counter),
                    run_time=0.3
                )
            
            current_voice_name = new_voice_name
            current_voice_info = new_voice_info
            self.counter = counter
            
            # 等待音频播放完成
            self.wait(2.5)
        
        # 结束
        self.play(
            FadeOut(current_voice_name),
            FadeOut(current_voice_info),
            FadeOut(self.counter),
            FadeOut(sample_text),
            run_time=0.5
        )
        
        # 结束文字
        end_text = Text(
            "展示完毕！",
            font="STKaiti",
            font_size=64,
            color=GREEN
        )
        
        self.play(Write(end_text), run_time=0.8)
        self.wait(1)
        
        self.play(
            FadeOut(title),
            FadeOut(underline),
            FadeOut(end_text),
            run_time=0.5
        )



if __name__ == "__main__":
    script_name = os.path.basename(__file__).replace(".py", "")
    # 运行语音展示动画
    os.system(f'cd "{script_dir}" && manimgl {script_name}.py VoiceShowcase -w')
