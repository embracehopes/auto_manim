/*
 * 复数解集可视化 Fragment Shader
 * 
 * 误差函数: F(x, y) = [x² + 5y² - 5] + i·[x² + (y-1)² - r²]
 * 其中 x ∈ ℂ (复平面坐标), y ∈ ℝ (实数参数)
 * 
 * 可视化策略:
 * - 固定 y 为实数参数 y_param
 * - 在 x 的复平面上绘图
 * - 计算 w = F(x, y_param)
 * - 颜色映射: arg(w) → Hue, |w| → Lightness
 * - 解集: 颜色极暗(接近黑)的点
 */

#version 330

// Uniform 参数
uniform float opacity;           // 透明度
uniform float y_param;           // y 参数 (实部)
uniform float y_imag;            // y 参数 (虚部扰动，用于打破退化)
uniform float r_param;           // r 参数 (圆的半径)
uniform float brightness_scale;  // 亮度缩放
uniform float saturation_scale;  // 饱和度缩放

// 输入输出
in vec3 xyz_coords;
out vec4 frag_color;

// 引入通用函数
#INSERT finalize_color.glsl

// ========== 常量 ==========
const float PI = 3.14159265359;

// ========== 复数运算函数 ==========

// 复数乘法: (a + bi) * (c + di) = (ac - bd) + (ad + bc)i
vec2 cmul(vec2 a, vec2 b) {
    return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

// ========== HSL 转 RGB ==========

vec3 hsl2rgb(float h, float s, float l) {
    h = mod(h, 1.0);
    float c = (1.0 - abs(2.0 * l - 1.0)) * s;
    float x_val = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));
    float m = l - c / 2.0;
    
    vec3 rgb;
    if (h < 1.0/6.0) rgb = vec3(c, x_val, 0.0);
    else if (h < 2.0/6.0) rgb = vec3(x_val, c, 0.0);
    else if (h < 3.0/6.0) rgb = vec3(0.0, c, x_val);
    else if (h < 4.0/6.0) rgb = vec3(0.0, x_val, c);
    else if (h < 5.0/6.0) rgb = vec3(x_val, 0.0, c);
    else rgb = vec3(c, 0.0, x_val);
    
    return rgb + m;
}

// ========== 复数到颜色映射 ==========

vec3 complex_to_color(vec2 w) {
    // 检查无穷/NaN
    if (!isnan(w.x) && !isnan(w.y) && !isinf(w.x) && !isinf(w.y)) {
        float arg_w = atan(w.y, w.x);
        float mod_w = length(w);
        
        // Hue: 辐角映射到 [0, 1]
        float hue = (arg_w + PI) / (2.0 * PI);
        
        // Saturation
        float saturation = saturation_scale;
        
        // Lightness: 模的对数映射，避免极端值
        // 接近0的模会产生接近黑色的效果
        float lightness = 1.0 - 1.0 / (1.0 + log(1.0 + mod_w * brightness_scale));
        lightness = clamp(lightness, 0.05, 0.95);
        
        return hsl2rgb(hue, saturation, lightness);
    } else {
        return vec3(0.0);  // 黑色表示无穷/NaN
    }
}

// ========== 误差函数计算 ==========
// F(x, y) = [x² + 5y² - 5] + i·[x² + (y-1)² - r²]
// 其中 x ∈ ℂ (复平面坐标), y = y_param (实数参数)

vec2 compute_F(vec2 x) {
    // x² = (x.x + x.y*i)² = (x.x² - x.y²) + 2*x.x*x.y*i
    vec2 x_squared = cmul(x, x);
    
    // 第一个方程: Re(x²) + 5y² - 5
    float real_part = x_squared.x + 5.0 * y_param * y_param - 5.0;
    
    // 第二个方程: Re(x²) + (y-1)² - r²
    float imag_part = x_squared.x + (y_param - 1.0) * (y_param - 1.0) - r_param * r_param;
    
    return vec2(real_part, imag_part);
}

void main() {
    // 获取复平面坐标 (作为复数 x)
    vec2 x = xyz_coords.xy;
    
    // 计算误差函数值 F(x, y_param)
    vec2 w = compute_F(x);
    
    // 映射到颜色
    vec3 color = complex_to_color(w);
    
    // 输出最终颜色
    frag_color = finalize_color(
        vec4(color, opacity),
        xyz_coords,
        vec3(0.0, 0.0, 1.0)
    );
}
