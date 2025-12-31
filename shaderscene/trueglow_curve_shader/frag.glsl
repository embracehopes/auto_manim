#version 330

/*
 * 辉光曲线片段着色器
 * 
 * 实现两层辉光效果：
 * 1. 白色核心 - 纯白色中心线
 * 2. 柔和过渡到原始颜色的高斯模糊辉光
 * 
 * 去掉了中间的白色高斯模糊区域，直接从白色核心过渡到彩色辉光
 */

uniform float glow_factor;
uniform float core_width_ratio;
uniform float white_core_ratio;
uniform float anti_alias_width;
uniform mat4 perspective;

in vec4 color;
in float scaled_aaw;
in vec3 point;
in vec3 to_cam;
in vec3 curve_center;
in float glow_width;
in vec2 uv_coords;
in float curve_segment_length;
in vec3 tangent_dir;
in float distance_to_curve;

out vec4 frag_color;

#INSERT finalize_color.glsl

/*
 * 高斯衰减函数
 */
float gaussian(float distance, float sigma) {
    float s = max(sigma, 0.001);
    return exp(-0.5 * (distance * distance) / (s * s));
}

/*
 * 平滑阶跃函数 - 用于创建柔和的过渡
 */
float smooth_threshold(float x, float edge0, float edge1) {
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

void main() {
    // 计算到曲线中心的归一化距离 [0, 1]
    float r = abs(uv_coords.y);
    
    // 超出边界则丢弃
    if (r > 1.0) discard;
    
    // 基础颜色
    vec3 base_color = color.rgb;
    float base_alpha = color.a;
    
    // === 两层辉光效果参数 ===
    // 白色核心区域半径
    float white_core = clamp(white_core_ratio, 0.02, 0.25);
    // 过渡区域结束位置
    float transition_end = clamp(core_width_ratio, white_core + 0.1, 0.5);
    
    // === 高斯参数 ===
    // 白色核心的高斯宽度（窄，集中在中心）
    float white_sigma = white_core * 1.2;
    // 彩色辉光的高斯宽度（宽，扩散到外围）
    float color_sigma = 0.4;
    
    // === 计算权重 ===
    
    // 白色核心权重 - 使用高斯衰减，中心最亮
    float white_weight = gaussian(r, white_sigma);
    
    // 彩色辉光权重 - 整体高斯分布
    float color_weight = gaussian(r, color_sigma);
    
    // === 颜色混合 ===
    // 关键：白色核心直接过渡到彩色，使用 mix 实现柔和过渡
    // 过渡因子：在核心区域为0（白色），在过渡区域逐渐变为1（彩色）
    float transition_factor = smooth_threshold(r, white_core * 0.5, transition_end);
    
    // 混合白色和原始颜色
    vec3 white = vec3(1.0);
    vec3 mixed_color = mix(white, base_color, transition_factor);
    
    // 应用辉光强度
    // 中心区域使用白色权重增强亮度
    float brightness_boost = mix(1.5, 1.0, transition_factor);
    vec3 final_color = mixed_color * brightness_boost;
    
    // === 计算透明度 ===
    // 整体高斯衰减
    float overall_falloff = pow(1.0 - r, glow_factor * 0.6);
    
    // 组合权重：白色核心 + 彩色辉光
    float combined_weight = white_weight * (1.0 - transition_factor) + color_weight * transition_factor;
    combined_weight = max(combined_weight, color_weight * 0.5);  // 确保外围也有辉光
    
    // 最终透明度
    float final_alpha = base_alpha * combined_weight * overall_falloff;
    
    // 增强中心亮度
    final_alpha *= mix(1.3, 1.0, transition_factor);
    
    // === 边缘平滑 ===
    float edge_smooth = 1.0 - smooth_threshold(r, 0.85, 1.0);
    final_alpha *= edge_smooth;
    
    // === 反锯齿 ===
    float derivative = max(fwidth(r), scaled_aaw);
    final_alpha *= smoothstep(1.0, 1.0 - derivative, r);
    
    // === 输出 ===
    frag_color = vec4(final_color, clamp(final_alpha, 0.0, 1.0));
    
    // === 智能丢弃暗像素 ===
    float luminance = dot(frag_color.rgb, vec3(0.299, 0.587, 0.114));
    float visibility = luminance * frag_color.a;
    
    // 丢弃几乎不可见的像素
    if (visibility < 0.005) discard;
    if (frag_color.a < 0.01) discard;
    
    // 边缘区域更严格的丢弃条件
    if (r > 0.9 && visibility < 0.02) discard;
    
    // 应用着色（如果启用）
    if (shading != vec3(0.0)) {
        vec3 curve_normal = normalize(cross(tangent_dir, to_cam));
        frag_color = finalize_color(frag_color, point, curve_normal);
    }
}

