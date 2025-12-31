/*
 * 光波可视化顶点着色器
 * 
 * 该顶点着色器负责处理几何变换和数据传递。
 * 
 * 功能：
 * 1. 接收顶点位置数据
 * 2. 将世界坐标传递给片段着色器
 * 3. 调用通用位置变换函数
 * 
 * 设计简洁：主要的计算工作在片段着色器中完成，
 * 这里只负责基础的几何处理。
 */

#version 330

// 输入：顶点位置（世界坐标）
in vec3 point;

// 输出：传递给片段着色器的位置信息
out vec3 frag_point;

// 包含通用的 OpenGL 位置变换函数
#INSERT emit_gl_Position.glsl

void main(){
    // 将顶点位置传递给片段着色器
    frag_point = point;
    
    // 执行标准的模型-视图-投影变换
    emit_gl_Position(point);
}