"""
SoundLibrary - ManimGL 动画音效映射库

管理动画类型与音效文件的映射关系，
支持 AutoScene 在 self.play() 时自动播放对应音效。

使用方法：
    from sound_library import SoundLibrary
    
    lib = SoundLibrary()
    sound = lib.get_sound("ShowCreation")  # 从对应文件夹随机返回音效
"""

import os
import json
import random
from typing import Dict, Optional, List


class SoundLibrary:
    """
    动画音效库管理器
    
    按动画类型分类管理音效文件，支持：
    - 从文件夹随机选择音效
    - 自动查找音效文件
    - 音效开关控制
    """
    
    # 动画类别映射（动画类名 -> 文件夹名）
    CATEGORY_MAPPING: Dict[str, str] = {
        # ==================== 创建类 (creation/) ====================
        "ShowPartial": "creation",
        "ShowCreation": "creation",
        "Uncreate": "creation",
        "DrawBorderThenFill": "creation",
        "Write": "creation",
        "ShowIncreasingSubsets": "creation",
        "ShowSubmobjectsOneByOne": "creation",
        "AddTextWordByWord": "creation",
        
        # ==================== 淡入淡出类 (fade/) ====================
        "Fade": "fade",
        "FadeIn": "fade",
        "FadeOut": "fade",
        "FadeInFromPoint": "fade",
        "FadeOutToPoint": "fade",
        "FadeTransform": "fade",
        "FadeTransformPieces": "fade",
        "VFadeIn": "fade",
        "VFadeOut": "fade",
        "VFadeInThenOut": "fade",
        
        # ==================== 生长类 (grow/) ====================
        "GrowFromPoint": "grow",
        "GrowFromCenter": "grow",
        "GrowFromEdge": "grow",
        "GrowArrow": "grow",
        "SpinInFromNothing": "grow",
        
        # ==================== 指示类 (indicate/) ====================
        "FocusOn": "indicate",
        "Indicate": "indicate",
        "Flash": "indicate",
        "CircleIndicate": "indicate",
        "ShowPassingFlash": "indicate",
        "VShowPassingFlash": "indicate",
        "FlashAround": "indicate",
        "FlashUnder": "indicate",
        "ShowCreationThenDestruction": "indicate",
        "ShowCreationThenFadeOut": "indicate",
        "AnimationOnSurroundingRectangle": "indicate",
        "ShowPassingFlashAround": "indicate",
        "ShowCreationThenDestructionAround": "indicate",
        "ShowCreationThenFadeAround": "indicate",
        "ApplyWave": "indicate",
        "WiggleOutThenIn": "indicate",
        "TurnInsideOut": "indicate",
        "FlashyFadeIn": "indicate",
        
        # ==================== 移动类 (movement/) ====================
        "Homotopy": "movement",
        "SmoothedVectorizedHomotopy": "movement",
        "ComplexHomotopy": "movement",
        "PhaseFlow": "movement",
        "MoveAlongPath": "movement",
        
        # ==================== 数字类 (number/) ====================
        "ChangingDecimal": "number",
        "ChangeDecimalToValue": "number",
        "CountInFrom": "number",
        
        # ==================== 旋转类 (rotation/) ====================
        "Rotating": "rotation",
        "Rotate": "rotation",
        
        # ==================== 变换类 (transform/) ====================
        "Transform": "transform",
        "ReplacementTransform": "transform",
        "TransformFromCopy": "transform",
        "MoveToTarget": "transform",
        "ApplyMethod": "transform",
        "ApplyPointwiseFunction": "transform",
        "ApplyPointwiseFunctionToCenter": "transform",
        "FadeToColor": "transform",
        "ScaleInPlace": "transform",
        "ShrinkToCenter": "transform",
        "Restore": "transform",
        "ApplyFunction": "transform",
        "ApplyMatrix": "transform",
        "ApplyComplexFunction": "transform",
        "CyclicReplace": "transform",
        "Swap": "transform",
        "TransformMatchingParts": "transform",
        "TransformMatchingShapes": "transform",
        "TransformMatchingStrings": "transform",
        "TransformMatchingTex": "transform",
        
        # ==================== 更新类 (misc/) ====================
        "UpdateFromFunc": "misc",
        "UpdateFromAlphaFunc": "misc",
        "MaintainPositionRelativeTo": "misc",
        
        # ==================== 组合类 (misc/) ====================
        "AnimationGroup": "misc",
        "Succession": "misc",
        "LaggedStart": "misc",
        "LaggedStartMap": "misc",
        
        # ==================== 特殊类 (misc/) ====================
        "Broadcast": "misc",
    }
    
    # 支持的音频扩展名
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a'}
    
    def __init__(self, library_path: str = None, config_path: str = None):
        """
        初始化音效库
        
        Args:
            library_path: 音效库根目录（默认 assets/sounds/library/）
            config_path: 自定义配置文件路径（可选）
        """
        # 设置音效库路径
        if library_path:
            self._library_path = library_path
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            self._library_path = os.path.join(parent_dir, "assets", "sounds", "library")
        
        # 类别映射
        self._category_mapping = self.CATEGORY_MAPPING.copy()
        
        # 加载自定义配置
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        # 音效开关
        self._enabled = True
        
        # 缓存文件夹内容（提高性能）
        self._folder_cache: Dict[str, List[str]] = {}
    
    def _load_config(self, config_path: str) -> None:
        """
        从 JSON 配置文件加载音效映射
        
        Args:
            config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_mapping = json.load(f)
                self._category_mapping.update(custom_mapping)
                print(f"✅ 加载音效配置: {config_path}")
        except Exception as e:
            print(f"⚠️ 加载音效配置失败: {e}")
    
    def _get_folder_files(self, folder_name: str) -> List[str]:
        """
        获取指定文件夹中的所有音效文件
        
        Args:
            folder_name: 文件夹名称
            
        Returns:
            音效文件路径列表
        """
        if folder_name in self._folder_cache:
            return self._folder_cache[folder_name]
        
        folder_path = os.path.join(self._library_path, folder_name)
        
        if not os.path.exists(folder_path):
            self._folder_cache[folder_name] = []
            return []
        
        files = []
        for filename in os.listdir(folder_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in self.AUDIO_EXTENSIONS:
                files.append(os.path.join(folder_path, filename))
        
        self._folder_cache[folder_name] = files
        return files
    
    def get_sound(self, animation_name: str, max_duration: float = None) -> Optional[str]:
        """
        获取动画对应的音效文件路径（从文件夹随机选择，优先选择较短的）
        
        Args:
            animation_name: 动画类名（如 "ShowCreation"）
            max_duration: 最大时长（秒），如果指定则优先选择较短的音效
            
        Returns:
            音效文件绝对路径，如果没有映射或文件不存在则返回 None
        """
        if not self._enabled:
            return None
        
        # 查找类别
        folder_name = self._category_mapping.get(animation_name)
        if not folder_name:
            return None
        
        # 获取文件夹中的文件
        files = self._get_folder_files(folder_name)
        
        if not files:
            return None
        
        # 如果只有一个文件，直接返回
        if len(files) == 1:
            return files[0]
        
        # 优先选择文件大小较小的（通常时长较短）
        # 按文件大小排序，取前半部分中随机选择
        try:
            sorted_files = sorted(files, key=lambda f: os.path.getsize(f))
            # 从较小的一半文件中随机选择
            half_count = max(1, len(sorted_files) // 2)
            return random.choice(sorted_files[:half_count])
        except:
            # 如果排序失败，回退到纯随机
            return random.choice(files)
    
    def get_add_sound(self) -> Optional[str]:
        """
        获取 add() 对应的音效文件路径（从 add/ 文件夹随机选择）
        
        Returns:
            音效文件绝对路径，如果文件夹为空则返回 None
        """
        if not self._enabled:
            return None
        
        files = self._get_folder_files("add")
        
        if not files:
            return None
        
        return random.choice(files)
    
    def get_random_from_folder(self, folder_name: str) -> Optional[str]:
        """
        从指定文件夹随机获取音效
        
        Args:
            folder_name: 文件夹名称
            
        Returns:
            音效文件路径
        """
        if not self._enabled:
            return None
        
        files = self._get_folder_files(folder_name)
        
        if not files:
            return None
        
        return random.choice(files)
    
    def set_enabled(self, enabled: bool) -> None:
        """启用/禁用音效"""
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        """音效是否启用"""
        return self._enabled
    
    def add_mapping(self, animation_name: str, folder_name: str) -> None:
        """
        添加自定义映射
        
        Args:
            animation_name: 动画类名
            folder_name: 文件夹名称
        """
        self._category_mapping[animation_name] = folder_name
    
    def get_library_path(self) -> str:
        """获取音效库根目录"""
        return self._library_path
    
    def get_all_mappings(self) -> Dict[str, str]:
        """获取所有映射"""
        return self._category_mapping.copy()
    
    def get_all_folders(self) -> List[str]:
        """获取所有可用的音效文件夹"""
        if not os.path.exists(self._library_path):
            return []
        
        folders = []
        for name in os.listdir(self._library_path):
            folder_path = os.path.join(self._library_path, name)
            if os.path.isdir(folder_path):
                folders.append(name)
        
        return sorted(folders)
    
    def clear_cache(self) -> None:
        """清除文件夹缓存（当添加新音效后调用）"""
        self._folder_cache.clear()
    
    def list_folder_contents(self, folder_name: str) -> List[str]:
        """
        列出文件夹中的所有音效文件名
        
        Args:
            folder_name: 文件夹名称
            
        Returns:
            文件名列表
        """
        files = self._get_folder_files(folder_name)
        return [os.path.basename(f) for f in files]
    
    def export_config(self, output_path: str) -> None:
        """
        导出当前映射为 JSON 配置文件
        
        Args:
            output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self._category_mapping, f, indent=2, ensure_ascii=False)
        print(f"📄 导出音效配置: {output_path}")


# ==================== 便捷函数 ====================

def create_library_structure(base_path: str) -> None:
    """
    创建音效库目录结构
    
    Args:
        base_path: 音效库根目录
    """
    folders = [
        "add",       # self.add() 专用
        "creation",
        "fade",
        "transform",
        "grow",
        "indicate",
        "movement",
        "rotation",
        "number",
        "misc"
    ]
    
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"📁 创建目录: {folder_path}")
    
    print(f"\n✅ 音效库结构创建完成: {base_path}")


if __name__ == "__main__":
    # 测试音效库
    lib = SoundLibrary()
    
    print("=== 音效库测试 ===")
    print(f"库路径: {lib.get_library_path()}")
    
    # 列出所有文件夹
    print(f"\n📁 可用文件夹: {lib.get_all_folders()}")
    
    # 测试随机获取音效
    print("\n🔊 测试随机音效:")
    test_anims = ["ShowCreation", "FadeIn", "GrowFromCenter", "Transform", "Flash"]
    for anim in test_anims:
        sound = lib.get_sound(anim)
        if sound:
            print(f"  {anim} -> {os.path.basename(sound)}")
        else:
            print(f"  {anim} -> (无音效)")
    
    # 测试 add 音效
    print("\n🔊 测试 add 音效:")
    add_sound = lib.get_add_sound()
    if add_sound:
        print(f"  add -> {os.path.basename(add_sound)}")
    else:
        print(f"  add -> (无音效)")
    
    # 列出各文件夹内容
    print("\n📂 文件夹内容:")
    for folder in lib.get_all_folders():
        contents = lib.list_folder_contents(folder)
        print(f"  {folder}/: {len(contents)} 个文件")
