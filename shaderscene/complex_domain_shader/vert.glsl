/*
 * 复变函数 Domain Coloring 顶点着色器
 * 
 * 功能：
 * 1. 接收顶点位置
 * 2. 根据 scale_factor 和 offset 变换坐标到复平面
 * 3. 将变换后的坐标传递给片段着色器
 */

#version 330

// 输入：顶点位置（世界坐标）
in vec3 point;
// manimlib 默认要求 rgba 属性（即使不使用）
in vec4 rgba;

// 输出：传递给片段着色器的复平面坐标
out vec3 xyz_coords;

// 缩放和偏移参数
uniform float scale_factor;  // 缩放因子
uniform vec3 offset;         // 偏移量（复平面中心点）

// 引入通用位置变换函数
#INSERT emit_gl_Position.glsl

void main() {
    // 计算复平面坐标
    xyz_coords = (point - offset) / scale_factor;
    
    // 执行标准的模型-视图-投影变换
    emit_gl_Position(point);
}
