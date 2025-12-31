"""
自定义虚线Mobject - GL版本
"""

from manimlib import *
import numpy as np


class MyDashMobject(VMobject):
    """GL版本的自定义虚线Mobject

    Parameters
    ----------
    vmobject : VMobject
        要转换为虚线的对象
    num_dashes : int
        虚线段数量，默认15
    dashed_ratio : float
        虚线占空比（实线部分比例），默认0.5
    dash_offset : float
        虚线起始位置偏移，默认0
    equal_lengths : bool
        是否使用等长虚线，默认True
    """

    def __init__(
        self,
        vmobject: VMobject,
        num_dashes: int = 15,
        dashed_ratio: float = 0.5,
        dash_offset: float = 0,
        equal_lengths: bool = True,
        **kwargs
    ):
        self.vmobject = vmobject
        self.num_dashes = num_dashes
        self.dashed_ratio = dashed_ratio
        self.dash_offset = dash_offset
        self.equal_lengths = equal_lengths

        # 调用父类构造函数
        super().__init__(**kwargs)

        # 创建虚线
        self._create_dashes()

    def _create_dashes(self):
        """创建虚线段"""
        r = self.dashed_ratio
        n = self.num_dashes

        if n <= 0:
            return

        # 计算虚线和空白的长度
        dash_len = r / n

        # 检查对象是否是封闭的
        is_closed = hasattr(self.vmobject, 'is_closed') and self.vmobject.is_closed()

        if is_closed:
            void_len = (1 - r) / n
        else:
            void_len = 1 - r if n == 1 else (1 - r) / (n - 1)

        period = dash_len + void_len
        phase_shift = (self.dash_offset % 1) * period

        # 计算虚线起始和结束位置
        if is_closed:
            pattern_len = 1
        else:
            pattern_len = 1 + void_len

        dash_starts = [((i * period + phase_shift) % pattern_len) for i in range(n)]
        dash_ends = [
            ((i * period + dash_len + phase_shift) % pattern_len) for i in range(n)
        ]

        # 处理开放曲线的边界情况
        if not is_closed:
            # 处理最后一个虚线段的溢出
            if dash_ends[-1] > 1 and dash_starts[-1] > 1:
                dash_ends.pop()
                dash_starts.pop()
            elif dash_ends[-1] < dash_len:
                if dash_starts[-1] < 1:
                    dash_starts.append(0)
                    dash_ends.append(dash_ends[-1])
                    dash_ends[-2] = 1
                else:
                    dash_starts[-1] = 0
            elif dash_starts[-1] > (1 - dash_len):
                dash_ends[-1] = 1

        # 创建虚线段
        if self.equal_lengths:
            self._create_equal_length_dashes(dash_starts, dash_ends)
        else:
            self._create_variable_length_dashes(dash_starts, dash_ends)

    def _create_equal_length_dashes(self, dash_starts, dash_ends):
        """创建等长虚线段"""
        # 检查对象是否有get_nth_curve_length_pieces方法
        if hasattr(self.vmobject, 'get_nth_curve_length_pieces') and hasattr(self.vmobject, 'get_num_curves'):
            try:
                # 计算曲线总长度
                norms = np.array([0])
                num_curves = self.vmobject.get_num_curves()
                for k in range(num_curves):
                    norms = np.append(norms, self.vmobject.get_nth_curve_length_pieces(k))

                length_vals = np.cumsum(norms)
                ref_points = np.linspace(0, 1, length_vals.size)
                curve_length = length_vals[-1]

                # 添加虚线段
                for i in range(len(dash_starts)):
                    start_t = np.interp(
                        dash_starts[i] * curve_length,
                        length_vals,
                        ref_points
                    )
                    end_t = np.interp(
                        dash_ends[i] * curve_length,
                        length_vals,
                        ref_points
                    )

                    dash_segment = self.vmobject.get_subcurve(start_t, end_t)
                    self.add(dash_segment)
            except Exception:
                # 如果出现任何错误，使用简化的实现
                self._create_equal_length_dashes_simple(dash_starts, dash_ends)
        else:
            # 如果没有相关方法，使用简化的等长实现
            self._create_equal_length_dashes_simple(dash_starts, dash_ends)

    def _create_equal_length_dashes_simple(self, dash_starts, dash_ends):
        """简化的等长虚线段创建方法"""
        # 对于没有get_nth_curve_length_pieces方法的对象，使用均匀分布
        for i in range(len(dash_starts)):
            # 直接使用参数t值，不进行长度补偿
            start_t = dash_starts[i]
            end_t = dash_ends[i]

            # 确保参数在有效范围内
            if start_t < end_t:
                dash_segment = self.vmobject.get_subcurve(start_t, end_t)
                self.add(dash_segment)

    def _create_variable_length_dashes(self, dash_starts, dash_ends):
        """创建变长虚线段"""
        for i in range(len(dash_starts)):
            dash_segment = self.vmobject.get_subcurve(
                dash_starts[i],
                dash_ends[i]
            )
            self.add(dash_segment)

    def copy(self):
        """复制对象"""
        return MyDashMobject(
            self.vmobject.copy(),
            num_dashes=self.num_dashes,
            dashed_ratio=self.dashed_ratio,
            dash_offset=self.dash_offset,
            equal_lengths=self.equal_lengths,
            **self.get_style_dict()
        )


