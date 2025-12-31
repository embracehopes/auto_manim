"""
自动换行工具模块 - 用于 ManimGL 的 Tex/Text 自动换行

核心功能：
1. 基于 .get_width() 的贪心断行算法
2. 支持中英文混排
3. 支持 Tex 和 Text 两种模式
4. 包含调试信息输出

使用方法：
    from auto_wrap import AutoWrap, wrap_text_to_width, wrap_tex_to_width
    
    # 方式1：使用便捷函数
    lines = wrap_text_to_width("很长的文本...", max_width=6.0)
    
    # 方式2：使用类（更多控制）
    wrapper = AutoWrap(max_width_ratio=0.95, debug=True)
    mob = wrapper.create_wrapped_text("很长的文本...")

作者：AutoScene 工具集
"""

import re
from typing import List, Tuple, Dict, Any, Union, Optional


class AutoWrap:
    """
    自动换行工具类
    
    支持两种模式：
    - Text 模式：使用 manimlib.Text，适合纯文本/字幕
    - Tex 模式：使用 manimlib.Tex，适合数学公式
    """
    
    def __init__(
        self,
        max_width_ratio: float = 0.95,
        max_width_absolute: float = None,
        frame_width: float = 6.75,  # 竖版视频默认宽度
        debug: bool = False,
        line_buff: float = 0.15,
        font_size: int = 24,
        font: str = "STKaiti",
    ):
        """
        初始化自动换行工具
        
        Args:
            max_width_ratio: 最大宽度占屏幕比例 (0.0-1.0)
            max_width_absolute: 最大绝对宽度（如果设置，会覆盖 ratio）
            frame_width: 屏幕宽度（Manim 坐标单位）
            debug: 是否输出调试信息
            line_buff: 行间距
            font_size: 字体大小
            font: 字体名称
        """
        self.max_width_ratio = max_width_ratio
        self.frame_width = frame_width
        self.debug = debug
        self.line_buff = line_buff
        self.font_size = font_size
        self.font = font
        
        # 计算最大宽度
        if max_width_absolute is not None:
            self.max_width = max_width_absolute
        else:
            self.max_width = max_width_ratio * frame_width
        
        # 缓存：避免重复编译相同文本
        self._width_cache: Dict[str, float] = {}
        
        # 统计信息
        self._stats = {
            "total_tokens": 0,
            "line_count": 0,
            "tex_compilations": 0,
            "cache_hits": 0,
        }
    
    def _log(self, msg: str):
        """输出调试信息"""
        if self.debug:
            print(f"[AutoWrap] {msg}")
    
    # ==================== Token 化 ====================
    
    def tokenize(self, text: str) -> List[str]:
        """
        将文本切分为 token 列表
        
        规则：
        - 中文：按单字切分
        - 英文/数字：按单词切分（空格分隔）
        - 标点：单独成 token
        - 数学符号：保持完整
        
        Args:
            text: 原始文本
            
        Returns:
            token 列表
        """
        # 预处理：标准化空格
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 分离常见标点（中英文都处理）
        punctuation = r'([,，.。;；:：!！?？、·\-\(\)\[\]（）【】「」『』《》<>])'
        text = re.sub(punctuation, r' \1 ', text)
        
        # 按空格初步分割
        parts = text.split()
        
        tokens = []
        for part in parts:
            if not part:
                continue
            
            # 检测是否包含中文
            has_chinese = bool(re.search(r'[\u4e00-\u9fff]', part))
            
            if has_chinese and len(part) > 1:
                # 中文：按字符切分，但保留英文单词完整
                i = 0
                while i < len(part):
                    char = part[i]
                    if re.match(r'[\u4e00-\u9fff]', char):
                        # 中文字符：单独成 token
                        tokens.append(char)
                        i += 1
                    elif re.match(r'[A-Za-z0-9]', char):
                        # 英文/数字：收集完整单词
                        word = char
                        i += 1
                        while i < len(part) and re.match(r'[A-Za-z0-9]', part[i]):
                            word += part[i]
                            i += 1
                        tokens.append(word)
                    else:
                        # 其他字符
                        tokens.append(char)
                        i += 1
            else:
                # 纯英文或单字符：直接添加
                tokens.append(part)
        
        self._stats["total_tokens"] = len(tokens)
        self._log(f"Token 化: {len(tokens)} 个 token")
        
        return tokens
    
    # ==================== 宽度测量 ====================
    
    def _measure_width_text(self, text: str, **kwargs) -> float:
        """
        测量 Text 对象宽度
        
        使用缓存避免重复创建对象
        """
        cache_key = f"text:{text}:{self.font_size}:{self.font}"
        
        if cache_key in self._width_cache:
            self._stats["cache_hits"] += 1
            return self._width_cache[cache_key]
        
        try:
            from manimlib import Text
            mob = Text(
                text,
                font=kwargs.get("font", self.font),
                font_size=kwargs.get("font_size", self.font_size),
            )
            width = mob.get_width()
            self._width_cache[cache_key] = width
            self._stats["tex_compilations"] += 1
            return width
        except Exception as e:
            self._log(f"测量 Text 宽度失败: {e}")
            # 估算：假设每个字符约 0.2 单位宽度
            return len(text) * 0.15
    
    def _measure_width_tex(self, tex_string: str, **kwargs) -> float:
        """
        测量 Tex 对象宽度
        
        注意：Tex 编译较慢，建议预处理时使用
        """
        cache_key = f"tex:{tex_string}:{kwargs.get('font_size', self.font_size)}"
        
        if cache_key in self._width_cache:
            self._stats["cache_hits"] += 1
            return self._width_cache[cache_key]
        
        try:
            from manimlib import Tex
            mob = Tex(
                tex_string,
                font_size=kwargs.get("font_size", self.font_size),
            )
            width = mob.get_width()
            self._width_cache[cache_key] = width
            self._stats["tex_compilations"] += 1
            return width
        except Exception as e:
            self._log(f"测量 Tex 宽度失败: {e}")
            return len(tex_string) * 0.12
    
    # ==================== Token 合并 ====================
    
    def _join_tokens(self, tokens: List[str]) -> str:
        """
        将 token 列表合并为字符串
        
        规则：
        - 中文字符之间不加空格
        - 英文单词之间加空格
        - 中英文交界处不加空格
        """
        if not tokens:
            return ""
        
        result = tokens[0]
        
        for i in range(1, len(tokens)):
            prev = tokens[i - 1]
            curr = tokens[i]
            
            # 判断是否需要空格
            prev_is_alnum = bool(re.match(r'^[A-Za-z0-9]+$', prev))
            curr_is_alnum = bool(re.match(r'^[A-Za-z0-9]+$', curr))
            
            # 只有前后都是英文/数字时才加空格
            if prev_is_alnum and curr_is_alnum:
                result += " " + curr
            else:
                result += curr
        
        return result
    
    # ==================== 贪心断行算法 ====================
    
    def wrap_tokens(
        self,
        tokens: List[str],
        mode: str = "text",
        **kwargs
    ) -> List[str]:
        """
        贪心断行：将 token 列表分成多行
        
        算法：
        1. 逐个添加 token 到当前行
        2. 每次测量当前行宽度
        3. 如果超过 max_width，则断行
        
        Args:
            tokens: token 列表
            mode: "text" 或 "tex"
            **kwargs: 传递给测量函数的参数
            
        Returns:
            行字符串列表
        """
        if not tokens:
            return []
        
        measure_func = (
            self._measure_width_text if mode == "text" 
            else self._measure_width_tex
        )
        
        lines = []
        current_tokens = []
        
        self._log(f"开始断行: max_width={self.max_width:.3f}, "
                  f"tokens={len(tokens)}")
        
        for i, token in enumerate(tokens):
            # 尝试添加当前 token
            trial_tokens = current_tokens + [token]
            trial_str = self._join_tokens(trial_tokens)
            trial_width = measure_func(trial_str, **kwargs)
            
            if self.debug and i % 10 == 0:
                self._log(f"  Token {i}: '{token}' | "
                         f"试探宽度: {trial_width:.3f} / {self.max_width:.3f}")
            
            if trial_width <= self.max_width or not current_tokens:
                # 未超过或当前行为空（强制添加）
                current_tokens = trial_tokens
            else:
                # 超过了，断行
                line_str = self._join_tokens(current_tokens)
                line_width = measure_func(line_str, **kwargs)
                lines.append(line_str)
                
                fill_ratio = line_width / self.max_width * 100
                self._log(f"  断行 #{len(lines)}: '{line_str[:20]}...' | "
                         f"宽度: {line_width:.3f} ({fill_ratio:.1f}%)")
                
                # 开始新行
                current_tokens = [token]
        
        # 处理最后一行
        if current_tokens:
            line_str = self._join_tokens(current_tokens)
            line_width = measure_func(line_str, **kwargs)
            lines.append(line_str)
            
            fill_ratio = line_width / self.max_width * 100
            self._log(f"  最后行 #{len(lines)}: '{line_str[:20]}...' | "
                     f"宽度: {line_width:.3f} ({fill_ratio:.1f}%)")
        
        self._stats["line_count"] = len(lines)
        self._log(f"断行完成: {len(lines)} 行")
        
        return lines
    
    # ==================== 创建 Mobject ====================
    
    def create_wrapped_text(
        self,
        text: str,
        align: str = "left",
        **kwargs
    ) -> "VGroup":
        """
        创建自动换行的 Text VGroup
        
        Args:
            text: 原始文本
            align: 对齐方式 ("left", "center", "right")
            **kwargs: 传递给 Text 的参数
            
        Returns:
            VGroup 包含多行 Text
        """
        from manimlib import Text, VGroup, LEFT, ORIGIN, DOWN
        
        # Token 化和断行
        tokens = self.tokenize(text)
        lines = self.wrap_tokens(tokens, mode="text", **kwargs)
        
        # 创建 Text 对象
        text_kwargs = {
            "font": kwargs.get("font", self.font),
            "font_size": kwargs.get("font_size", self.font_size),
        }
        # 合并其他 kwargs
        for k, v in kwargs.items():
            if k not in text_kwargs:
                text_kwargs[k] = v
        
        mobs = [Text(line, **text_kwargs) for line in lines]
        
        # 排列
        aligned_edge = LEFT if align == "left" else ORIGIN
        group = VGroup(*mobs)
        group.arrange(DOWN, aligned_edge=aligned_edge, buff=self.line_buff)
        
        self._log(f"创建 Text VGroup: {len(mobs)} 行")
        self._print_stats()
        
        return group
    
    def create_wrapped_tex(
        self,
        tex_string: str,
        align: str = "left",
        **kwargs
    ) -> "VGroup":
        """
        创建自动换行的 Tex VGroup
        
        注意：对于复杂数学公式，建议手动断行
        
        Args:
            tex_string: LaTeX 字符串
            align: 对齐方式
            **kwargs: 传递给 Tex 的参数
            
        Returns:
            VGroup 包含多行 Tex
        """
        from manimlib import Tex, VGroup, LEFT, ORIGIN, DOWN
        
        # Token 化和断行
        tokens = self.tokenize(tex_string)
        lines = self.wrap_tokens(tokens, mode="tex", **kwargs)
        
        # 创建 Tex 对象
        tex_kwargs = {
            "font_size": kwargs.get("font_size", self.font_size),
        }
        for k, v in kwargs.items():
            if k not in tex_kwargs:
                tex_kwargs[k] = v
        
        mobs = [Tex(line, **tex_kwargs) for line in lines]
        
        # 排列
        aligned_edge = LEFT if align == "left" else ORIGIN
        group = VGroup(*mobs)
        group.arrange(DOWN, aligned_edge=aligned_edge, buff=self.line_buff)
        
        self._log(f"创建 Tex VGroup: {len(mobs)} 行")
        self._print_stats()
        
        return group
    
    def _print_stats(self):
        """打印统计信息"""
        if self.debug:
            print(f"[AutoWrap 统计]")
            print(f"  总 Token 数: {self._stats['total_tokens']}")
            print(f"  行数: {self._stats['line_count']}")
            print(f"  编译次数: {self._stats['tex_compilations']}")
            print(f"  缓存命中: {self._stats['cache_hits']}")
            print(f"  缓存命中率: {self._stats['cache_hits'] / max(1, self._stats['tex_compilations'] + self._stats['cache_hits']) * 100:.1f}%")


# ==================== 便捷函数 ====================

def wrap_text_to_width(
    text: str,
    max_width: float = None,
    max_width_ratio: float = 0.95,
    frame_width: float = 6.75,
    debug: bool = False,
    **kwargs
) -> List[str]:
    """
    将文本按宽度自动断行（便捷函数）
    
    Args:
        text: 原始文本
        max_width: 最大宽度（绝对值）
        max_width_ratio: 最大宽度比例（相对于 frame_width）
        frame_width: 屏幕宽度
        debug: 是否输出调试信息
        **kwargs: 传递给测量函数
        
    Returns:
        行字符串列表
    """
    wrapper = AutoWrap(
        max_width_ratio=max_width_ratio,
        max_width_absolute=max_width,
        frame_width=frame_width,
        debug=debug,
        **{k: v for k, v in kwargs.items() if k in ["font_size", "font", "line_buff"]}
    )
    
    tokens = wrapper.tokenize(text)
    return wrapper.wrap_tokens(tokens, mode="text", **kwargs)


def wrap_tex_to_width(
    tex_string: str,
    max_width: float = None,
    max_width_ratio: float = 0.95,
    frame_width: float = 6.75,
    debug: bool = False,
    **kwargs
) -> List[str]:
    """
    将 Tex 字符串按宽度自动断行（便捷函数）
    
    Args:
        tex_string: LaTeX 字符串
        max_width: 最大宽度（绝对值）
        max_width_ratio: 最大宽度比例
        frame_width: 屏幕宽度
        debug: 是否输出调试信息
        **kwargs: 传递给测量函数
        
    Returns:
        行字符串列表
    """
    wrapper = AutoWrap(
        max_width_ratio=max_width_ratio,
        max_width_absolute=max_width,
        frame_width=frame_width,
        debug=debug,
        **{k: v for k, v in kwargs.items() if k in ["font_size", "line_buff"]}
    )
    
    tokens = wrapper.tokenize(tex_string)
    return wrapper.wrap_tokens(tokens, mode="tex", **kwargs)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("AutoWrap 自动换行测试")
    print("=" * 60)
    
    # 测试文本
    test_texts = [
        "这是一个很长的中文文本示例，用于测试超过屏幕宽度95%之后自动换行的逻辑。",
        "We also test English text wrapping to see if it works correctly.",
        "混合测试：这是中英文mixed的文本，包含English words和中文字符。",
        "数学公式测试：设集合P={-1,0,1,2,3,4}，从P取整数a，从Q取整数b，求概率。",
    ]
    
    print("\n--- 纯 Token 化测试（无 ManimGL 依赖）---\n")
    
    wrapper = AutoWrap(
        max_width_ratio=0.95,
        frame_width=6.75,
        debug=True,
    )
    
    for i, text in enumerate(test_texts):
        print(f"\n测试 {i+1}: {text[:30]}...")
        tokens = wrapper.tokenize(text)
        print(f"  Tokens: {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
        print(f"  Token 数: {len(tokens)}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("如需完整测试（包含宽度测量），请在 ManimGL 环境中运行。")
    print("=" * 60)
