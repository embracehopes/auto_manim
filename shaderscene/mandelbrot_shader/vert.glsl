/*
 * Mandelbrot 分形顶点着色器
 * 
 * 功能：
 * 1. 接收顶点位置
 * 2. 根据 scale_factor 和 offset 变换坐标
 * 3. 将变换后的坐标传递给片段着色器
 * 
 * 坐标变换说明：
 * xyz_coords = (point - offset) / scale_factor
 * 
 * 这样可以通过修改 offset 和 scale_factor 实现：
 * - 平移（改变 offset）
 * - 缩放（改变 scale_factor）
 */

#version 330

// 输入：顶点位置（世界坐标）
in vec3 point;

// 输出：传递给片段着色器的复平面坐标
out vec3 xyz_coords;

// 缩放和偏移参数
uniform float scale_factor;  // 缩放因子（越小看到的区域越小，即放大）
uniform vec3 offset;         // 偏移量（复平面中心点）

// 引入通用位置变换函数
#INSERT emit_gl_Position.glsl

void main() {
    // 计算复平面坐标
    // (point - offset) / scale_factor 将屏幕坐标映射到复平面
    xyz_coords = (point - offset) / scale_factor;
    
    // 执行标准的模型-视图-投影变换
    emit_gl_Position(point);
}
