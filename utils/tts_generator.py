"""
TTS 配音生成工具
使用 edge-tts 生成高质量中文配音

使用方法:
    from tts_generator import TTSGenerator
    
    tts = TTSGenerator()
    await tts.generate("你好世界", "output.mp3")
"""

import asyncio
import os
import edge_tts


class TTSGenerator:
    """
    TTS 配音生成器
    
    中文语音推荐:
    - zh-CN-XiaoxiaoNeural: 女声（活泼）- 科普视频
    - zh-CN-YunxiNeural: 男声（自然）- 教学视频  
    - zh-CN-YunjianNeural: 男声（沉稳）- 专业讲解
    - zh-CN-XiaoyiNeural: 女声（甜美）- 故事讲述
    """
    
    # 默认语音
    DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
    
    def __init__(self, voice: str = None, rate: str = "+0%", pitch: str = "+0Hz"):
        """
        初始化 TTS 生成器
        
        Args:
            voice: 语音名称（默认 zh-CN-XiaoxiaoNeural）
            rate: 语速调节（如 "+10%", "-20%"）
            pitch: 音调调节（如 "+5Hz", "-10Hz"）
        """
        self.voice = voice or self.DEFAULT_VOICE
        self.rate = rate
        self.pitch = pitch
    
    async def generate(self, text: str, output_path: str) -> str:
        """
        生成配音文件
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径（支持 mp3, wav）
            
        Returns:
            输出文件的绝对路径
        """
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        await communicate.save(output_path)
        return os.path.abspath(output_path)
    
    async def generate_with_subtitle(
        self, 
        text: str, 
        audio_path: str, 
        subtitle_path: str = None
    ) -> tuple:
        """
        生成配音和字幕文件
        
        Args:
            text: 要转换的文本
            audio_path: 输出音频文件路径
            subtitle_path: 输出字幕文件路径（默认同名 .srt）
            
        Returns:
            (音频路径, 字幕路径)
        """
        if subtitle_path is None:
            base = os.path.splitext(audio_path)[0]
            subtitle_path = base + ".srt"
        
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        
        os.makedirs(os.path.dirname(os.path.abspath(audio_path)), exist_ok=True)
        
        submaker = edge_tts.SubMaker()
        
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)
        
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write(submaker.generate_subs())
        
        return os.path.abspath(audio_path), os.path.abspath(subtitle_path)
    
    async def generate_batch(
        self, 
        subtitles: list, 
        output_dir: str,
        prefix: str = "line"
    ) -> list:
        """
        批量生成配音文件
        
        Args:
            subtitles: 字幕列表 [{"text": "...", "id": 1}, ...]
            output_dir: 输出目录
            prefix: 文件名前缀
            
        Returns:
            生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for i, sub in enumerate(subtitles):
            text = sub.get("text", sub) if isinstance(sub, dict) else sub
            idx = sub.get("id", i + 1) if isinstance(sub, dict) else i + 1
            
            output_path = os.path.join(output_dir, f"{prefix}_{idx:03d}.mp3")
            await self.generate(text, output_path)
            results.append(output_path)
            print(f"✅ 生成: {output_path}")
        
        return results
    
    @staticmethod
    async def list_voices(language: str = "zh") -> list:
        """
        列出可用语音
        
        Args:
            language: 语言过滤（如 "zh", "en"）
            
        Returns:
            语音列表
        """
        voices = await edge_tts.list_voices()
        if language:
            voices = [v for v in voices if language.lower() in v["Locale"].lower()]
        return voices
    
    @staticmethod
    def list_voices_sync(language: str = "zh") -> list:
        """同步版本的 list_voices"""
        return asyncio.run(TTSGenerator.list_voices(language))


# ==================== 便捷函数 ====================

def generate_voice(text: str, output_path: str, voice: str = None) -> str:
    """
    快速生成配音（同步版本）
    
    Args:
        text: 文本内容
        output_path: 输出路径
        voice: 语音（可选）
        
    Returns:
        输出文件路径
    """
    tts = TTSGenerator(voice=voice)
    return asyncio.run(tts.generate(text, output_path))


def generate_voice_batch(subtitles: list, output_dir: str, voice: str = None) -> list:
    """
    批量生成配音（同步版本）
    
    Args:
        subtitles: 字幕列表
        output_dir: 输出目录
        voice: 语音（可选）
        
    Returns:
        输出文件路径列表
    """
    tts = TTSGenerator(voice=voice)
    return asyncio.run(tts.generate_batch(subtitles, output_dir))


# ==================== 测试 ====================

if __name__ == "__main__":
    import sys
    
    # 设置输出目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    sounds_dir = os.path.join(project_root, "assets", "sounds")
    
    print("=" * 50)
    print("🎤 TTS 配音生成器测试")
    print("=" * 50)
    
    # 列出中文语音
    print("\n📋 可用中文语音:")
    voices = TTSGenerator.list_voices_sync("zh-CN")
    for v in voices[:8]:  # 只显示前8个
        print(f"  - {v['ShortName']}: {v['Gender']}")
    
    # 生成测试配音
    print("\n🔊 生成测试配音...")
    test_texts = [
        "欢迎观看本期视频",
        "今天我们来学习勾股定理",
        "感谢收看，下期再见"
    ]
    
    output_files = generate_voice_batch(
        test_texts,
        sounds_dir,
        voice="zh-CN-XiaoxiaoNeural"
    )
    
    print("\n✅ 生成完成！")
    print(f"📁 输出目录: {sounds_dir}")
    for f in output_files:
        print(f"  - {os.path.basename(f)}")
