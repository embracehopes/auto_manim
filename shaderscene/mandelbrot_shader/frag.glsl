/*
 * Mandelbrot 分形 Fragment Shader
 * 
 * 实现 Mandelbrot 集和 Julia 集的可视化渲染
 * 
 * 数学原理：
 * - Mandelbrot集：z_{n+1} = z_n^2 + c，初始 z_0 = 0，c 为复平面坐标
 * - Julia集：z_{n+1} = z_n^2 + c，c 为固定参数，z_0 为复平面坐标
 * - 逃逸判定：|z| > 2 时认为发散
 * 
 * 着色技术：
 * - 使用平滑颜色映射避免条带
 * - 9色渐变调色盘
 * - 支持动态迭代次数
 */

#version 330

// Uniform 参数
uniform vec2 parameter;     // Julia集参数 c（mandelbrot模式时无效）
uniform float opacity;      // 透明度
uniform float n_steps;      // 迭代次数
uniform float mandelbrot;   // 1.0 = Mandelbrot集, 0.0 = Julia集

// 颜色映射（9种颜色）
uniform vec3 color0;
uniform vec3 color1;
uniform vec3 color2;
uniform vec3 color3;
uniform vec3 color4;
uniform vec3 color5;
uniform vec3 color6;
uniform vec3 color7;
uniform vec3 color8;

// 输入输出
in vec3 xyz_coords;         // 从顶点着色器传入的坐标
out vec4 frag_color;        // 输出颜色

// 引入通用函数
#INSERT finalize_color.glsl
#INSERT complex_functions.glsl

// float_to_color 函数已在 finalize_color.glsl 中定义

void main() {
    // 构建颜色映射数组
    vec3 color_map[9] = vec3[9](
        color0, color1, color2, color3,
        color4, color5, color6, color7, color8
    );
    
    vec3 color;
    vec2 z;
    vec2 c;

    // 根据模式设置初始值
    if (bool(mandelbrot)) {
        // Mandelbrot模式：c = 屏幕坐标，z = 0
        c = xyz_coords.xy;
        z = vec2(0.0, 0.0);
    } else {
        // Julia模式：c = 参数，z = 屏幕坐标
        c = parameter;
        z = xyz_coords.xy;
    }

    // 逃逸半径
    float outer_bound = 2.0;
    bool stable = true;
    
    // 迭代计算
    for (int n = 0; n < int(n_steps); n++) {
        // z = z^2 + c
        z = complex_mult(z, z) + c;
        
        // 逃逸判定
        if (length(z) > outer_bound) {
            float float_n = float(n);
            
            // 平滑着色：使用对数插值避免条带效应
            float_n += log(outer_bound) / log(length(z));
            
            // 添加基于c的微扰，增加颜色变化
            float_n += 0.5 * length(c);
            
            // 映射到颜色
            color = float_to_color(sqrt(float_n), 1.5, 8.0, color_map);
            stable = false;
            break;
        }
    }
    
    // 集合内部 - 黑色
    if (stable) {
        color = vec3(0.0, 0.0, 0.0);
    }

    // 输出最终颜色
    frag_color = finalize_color(
        vec4(color, opacity),
        xyz_coords,
        vec3(0.0, 0.0, 1.0)
    );
}
