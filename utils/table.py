"""
Table 类 - 使用 ManimGL API 实现
用于创建表格布局的工具类
"""

from manimlib import *
import numpy as np


class Table(VGroup):
    """
    表格类 - 用于创建和显示表格
    
    使用示例:
        table = Table(
            table_data,
            row_labels=[Text("行1"), Text("行2")],
            col_labels=[Text("列1"), Text("列2")],
            include_outer_lines=True,
            v_buff=0.5,
            h_buff=0.8
        )
    """
    
    def __init__(
        self,
        table_data,
        row_labels=None,
        col_labels=None,
        include_outer_lines=True,
        line_config=None,
        v_buff=0.4,
        h_buff=0.6,
        element_to_mobject=lambda x: x if isinstance(x, Mobject) else Text(str(x)),
        max_cell_width=None,
        max_cell_height=None,
        arrange_in_grid_config=None,
        **kwargs
    ):
        """
        参数:
            table_data: 二维列表，每个元素可以是 Mobject 或字符串
            row_labels: 行标签列表（可选）
            col_labels: 列标签列表（可选）
            include_outer_lines: 是否包含外边框
            line_config: 线条配置字典
            v_buff: 垂直间距
            h_buff: 水平间距
            element_to_mobject: 将非 Mobject 元素转换为 Mobject 的函数
            arrange_in_grid_config: 网格排列配置
        """
        super().__init__(**kwargs)
        
        self.table_data = table_data
        self.row_labels = row_labels
        self.col_labels = col_labels
        self.v_buff = v_buff
        self.h_buff = h_buff
        # 限制单元格尺寸（可选）
        self.max_cell_width = max_cell_width
        self.max_cell_height = max_cell_height
        self.element_to_mobject = element_to_mobject
        
        # 默认线条配置
        self.line_config = line_config or {
            "stroke_width": 2,
            "color": WHITE
        }
        
        # 默认网格配置
        self.arrange_in_grid_config = arrange_in_grid_config or {}
        
        # 存储所有单元格
        self.elements = VGroup()
        self.lines = VGroup()
        
        # 创建表格
        self._create_table(include_outer_lines)
    
    def _create_table(self, include_outer_lines):
        """创建表格主体"""
        # 转换所有数据为 Mobject
        rows = len(self.table_data)
        cols = len(self.table_data[0]) if rows > 0 else 0
        
        # 创建单元格网格
        for i, row in enumerate(self.table_data):
            row_group = VGroup()
            for j, cell in enumerate(row):
                if isinstance(cell, Mobject):
                    element = cell
                else:
                    element = self.element_to_mobject(cell)
                # Ensure element is a VMobject (VGroup) so VGroup.add accepts it
                if isinstance(element, VMobject):
                    safe_element = element
                elif isinstance(element, Mobject):
                    # Try to extract VMobject submobjects into a VGroup
                    submobs = [sm for sm in getattr(element, 'submobjects', []) if isinstance(sm, VMobject)]
                    if len(submobs) > 0:
                        safe_element = VGroup(*submobs)
                    else:
                        # Fallback: convert textual representation to a Text VMobject
                        safe_element = VGroup(self.element_to_mobject(str(cell)))
                else:
                    # Non-mobject fallback
                    safe_element = VGroup(self.element_to_mobject(cell))

                row_group.add(safe_element)
            self.elements.add(row_group)
        
        # 首先水平排列每一行
        for row_group in self.elements:
            row_group.arrange(RIGHT, buff=self.h_buff)
        
        # 然后垂直排列所有行
        # 如果设置了单元格最大尺寸，先对元素进行缩放以适配
        if self.max_cell_width is not None or self.max_cell_height is not None:
            for i, row_group in enumerate(self.elements):
                for j, cell in enumerate(row_group):
                    target_w = None
                    target_h = None
                    if self.max_cell_width is not None:
                        target_w = max(0.1, self.max_cell_width - 2 * self.h_buff)
                    if self.max_cell_height is not None:
                        target_h = max(0.1, self.max_cell_height - 2 * self.v_buff)
                    scale = 1.0
                    if target_w is not None and cell.get_width() > target_w:
                        scale = min(scale, float(target_w / cell.get_width()))
                    if target_h is not None and cell.get_height() > target_h:
                        scale = min(scale, float(target_h / cell.get_height()))
                    if scale < 1.0:
                        cell.scale(scale)
        self.elements.arrange(DOWN, buff=self.v_buff, aligned_edge=LEFT)
        
        # 对齐列：确保每列的元素在同一垂直线上
        for j in range(cols):
            # 找出这一列所有单元格
            col_cells = [self.elements[i][j] for i in range(rows)]
            # 找出这一列最宽的单元格
            max_width = max([cell.get_width() for cell in col_cells])
            # 计算这一列的中心 x 坐标（使用第一行的位置）
            col_x = col_cells[0].get_center()[0]
            # 将该列所有单元格对齐到同一 x 坐标
            for cell in col_cells:
                cell.move_to([col_x, cell.get_y(), 0])
        
        # 添加列标签（如果有）
        if self.col_labels:
            col_label_group = VGroup()
            for label in self.col_labels:
                if isinstance(label, Mobject):
                    col_label_group.add(label)
                else:
                    col_label_group.add(self.element_to_mobject(label))
            
            col_label_group.arrange(RIGHT, buff=self.h_buff)
            col_label_group.next_to(self.elements, UP, buff=self.v_buff)
            
            # 对齐列标签与数据列
            for i, label in enumerate(col_label_group):
                if i < len(self.elements[0]):
                    label.move_to(self.elements[0][i].get_center() + UP * (self.v_buff + label.get_height() / 2))
            
            self.col_labels_mobjects = col_label_group
            self.add(col_label_group)
        
        # 添加行标签（如果有）
        if self.row_labels:
            row_label_group = VGroup()
            for label in self.row_labels:
                if isinstance(label, Mobject):
                    row_label_group.add(label)
                else:
                    row_label_group.add(self.element_to_mobject(label))
            
            row_label_group.arrange(DOWN, buff=self.v_buff)
            row_label_group.next_to(self.elements, LEFT, buff=self.h_buff)
            
            # 对齐行标签与数据行
            for i, label in enumerate(row_label_group):
                if i < len(self.elements):
                    label.move_to(self.elements[i].get_center() + LEFT * (self.h_buff + label.get_width() / 2))
            
            self.row_labels_mobjects = row_label_group
            self.add(row_label_group)
        
        # 添加单元格到 VGroup
        self.add(self.elements)
        
        # 绘制网格线
        if include_outer_lines:
            self._draw_lines()
    
    def _draw_lines(self):
        """绘制表格线条"""
        if len(self.elements) == 0:
            return
        
        rows = len(self.elements)
        cols = len(self.elements[0])
        
        # 添加 padding 以便线条不会紧贴文字
        padding = 0.15
        
        # 获取每个单元格的边界
        x_positions = []  # 垂直线的 x 坐标
        y_positions = []  # 水平线的 y 坐标
        
        # 计算垂直线位置（基于列）
        for j in range(cols + 1):
            if j == 0:
                x = min([row[0].get_left()[0] for row in self.elements]) - padding
            elif j == cols:
                x = max([row[-1].get_right()[0] for row in self.elements]) + padding
            else:
                # 取第 j-1 列的右边和第 j 列的左边的中点
                x = (max([row[j-1].get_right()[0] for row in self.elements]) + 
                     min([row[j].get_left()[0] for row in self.elements])) / 2
            x_positions.append(x)
        
        # 计算水平线位置（基于行）
        for i in range(rows + 1):
            if i == 0:
                y = max([self.elements[0][j].get_top()[1] for j in range(len(self.elements[0]))]) + padding
            elif i == rows:
                y = min([self.elements[-1][j].get_bottom()[1] for j in range(len(self.elements[-1]))]) - padding
            else:
                # 取第 i-1 行的底部和第 i 行的顶部的中点
                y = (min([self.elements[i-1][j].get_bottom()[1] for j in range(len(self.elements[i-1]))]) + 
                     max([self.elements[i][j].get_top()[1] for j in range(len(self.elements[i]))])) / 2
            y_positions.append(y)
        
        # 绘制水平线
        for y in y_positions:
            h_line = Line(
                start=np.array([x_positions[0], y, 0]),
                end=np.array([x_positions[-1], y, 0]),
                **self.line_config
            )
            self.lines.add(h_line)
        
        # 绘制垂直线
        for x in x_positions:
            v_line = Line(
                start=np.array([x, y_positions[0], 0]),
                end=np.array([x, y_positions[-1], 0]),
                **self.line_config
            )
            self.lines.add(v_line)
        
        self.add(self.lines)
    
    def get_cell(self, row, col):
        """获取指定单元格"""
        if 0 <= row < len(self.elements) and 0 <= col < len(self.elements[row]):
            return self.elements[row][col]
        return None
    
    def get_row(self, row):
        """获取指定行"""
        if 0 <= row < len(self.elements):
            return self.elements[row]
        return None
    
    def get_col(self, col):
        """获取指定列"""
        column = VGroup()
        for row in self.elements:
            if 0 <= col < len(row):
                column.add(row[col])
        return column
    
    def get_entries(self):
        """获取所有单元格"""
        return self.elements
    
    def get_horizontal_lines(self):
        """获取所有水平线"""
        return VGroup(*[line for line in self.lines if abs(line.get_start()[1] - line.get_end()[1]) < 0.01])
    
    def get_vertical_lines(self):
        """获取所有垂直线"""
        return VGroup(*[line for line in self.lines if abs(line.get_start()[0] - line.get_end()[0]) < 0.01])
    
    def add_highlighted_cell(self, row, col, color=YELLOW, opacity=0.3, buff=0.1, **kwargs):
        """高亮指定单元格（添加背景矩形）"""
        cell = self.get_cell(row, col)
        if cell:
            # 创建填充矩形作为背景
            rect = Rectangle(
                width=cell.get_width() + 2 * buff,
                height=cell.get_height() + 2 * buff,
                fill_color=color,
                fill_opacity=opacity,
                stroke_width=0,
                **kwargs
            )
            rect.move_to(cell)
            # 将背景矩形插入到最底层
            self.submobjects.insert(0, rect)
            return rect
        return None


class MathTable(Table):
    """
    数学表格 - 专门用于显示数学表达式的表格
    默认使用 Tex 来渲染单元格内容
    """
    
    def __init__(
        self,
        table_data,
        element_to_mobject=lambda x: Tex(str(x)) if not isinstance(x, Mobject) else x,
        **kwargs
    ):
        super().__init__(
            table_data,
            element_to_mobject=element_to_mobject,
            **kwargs
        )


class DecimalTable(Table):
    """
    十进制数表格 - 专门用于显示数字的表格
    默认使用 DecimalNumber 来渲染单元格内容
    """
    
    def __init__(
        self,
        table_data,
        element_to_mobject=lambda x: DecimalNumber(float(x)) if not isinstance(x, Mobject) else x,
        **kwargs
    ):
        super().__init__(
            table_data,
            element_to_mobject=element_to_mobject,
            **kwargs
        )


class IntegerTable(Table):
    """
    整数表格 - 专门用于显示整数的表格
    默认使用 Integer 来渲染单元格内容
    """
    
    def __init__(
        self,
        table_data,
        element_to_mobject=lambda x: Integer(int(x)) if not isinstance(x, Mobject) else x,
        **kwargs
    ):
        super().__init__(
            table_data,
            element_to_mobject=element_to_mobject,
            **kwargs
        )
