#version 330

/*
 * 辉光包裹效果片段着色器
 * 
 * 实现两层辉光效果：
 * 1. 白色核心 - 纯白色中心
 * 2. 柔和过渡到原始颜色的高斯模糊辉光
 * 
 * 去掉了中间的白色高斯模糊区域，直接从白色核心过渡到彩色辉光
 */

uniform float glow_factor;
uniform float core_width_ratio;
uniform float white_core_ratio;
uniform float white_glow_ratio;

in vec4 color;
in vec2 uv;
in float scaled_aaw;

out vec4 frag_color;

// This include a declaration of uniform vec3 shading
#INSERT finalize_color.glsl

/*
 * 高斯衰减函数
 */
float gaussian(float distance, float sigma) {
    float s = max(sigma, 0.001);
    return exp(-0.5 * (distance * distance) / (s * s));
}

/*
 * 平滑阶跃函数
 */
float smooth_threshold(float x, float edge0, float edge1) {
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

void main(){
    // 计算到中心的归一化距离 [0, 1]
    float r = length(uv) / 1.41421356; // map square to unit disk
    
    if(r > 1.0){
        discard;
    }

    // 基础颜色
    vec3 base_color = color.rgb;
    float base_alpha = color.a;
    
    // === 两层辉光效果参数 ===
    // 白色核心区域半径（受 white_core_ratio 控制）
    float white_core = clamp(white_core_ratio * 0.3, 0.02, 0.2);
    // 过渡区域结束位置（受 core_width_ratio 控制）
    float transition_end = clamp(core_width_ratio * 0.6, white_core + 0.1, 0.45);
    
    // === 高斯参数 ===
    // 白色核心的高斯宽度（窄，集中在中心）
    float white_sigma = white_core * 1.5;
    // 彩色辉光的高斯宽度（宽，扩散到外围）
    float color_sigma = 0.35;
    
    // === 计算权重 ===
    
    // 白色核心权重 - 使用高斯衰减，中心最亮
    float white_weight = gaussian(r, white_sigma);
    
    // 彩色辉光权重 - 整体高斯分布
    float color_weight = gaussian(r, color_sigma);
    
    // === 颜色混合 ===
    // 过渡因子：在核心区域为0（白色），在过渡区域逐渐变为1（彩色）
    float transition_factor = smooth_threshold(r, white_core * 0.5, transition_end);
    
    // 如果 white_glow_ratio 为 0，则完全使用彩色（不显示白色核心）
    // 如果 white_glow_ratio 为 1，则完全按照上述逻辑混合
    float effective_white = white_weight * white_glow_ratio;
    float effective_transition = mix(1.0, transition_factor, white_glow_ratio);
    
    // 混合白色和原始颜色
    vec3 white = vec3(1.0);
    vec3 mixed_color = mix(white, base_color, effective_transition);
    
    // 应用辉光强度 - 中心区域增强亮度
    float brightness_boost = mix(1.4, 1.0, effective_transition);
    vec3 final_color = mixed_color * brightness_boost;
    
    // === 计算透明度 ===
    // 整体高斯衰减
    float overall_falloff = pow(1.0 - r, max(glow_factor, 0.5));
    
    // 组合权重
    float combined_weight = effective_white * (1.0 - effective_transition) + color_weight * effective_transition;
    combined_weight = max(combined_weight, color_weight * 0.5);
    
    // 最终透明度
    float final_alpha = base_alpha * combined_weight * overall_falloff;
    
    // 增强中心亮度
    final_alpha *= mix(1.3, 1.0, effective_transition);
    
    // 平滑 alpha 曲线
    float smooth_alpha = smoothstep(0.0, 1.0, final_alpha);

    frag_color = vec4(final_color, smooth_alpha);

    frag_color = finalize_color(frag_color, vec3(0.0), vec3(0.0));

    // 边缘平滑
    float edge = smoothstep(1.0, 1.0 - scaled_aaw, r);
    frag_color.a *= edge;

    if(frag_color.a <= 0.001){
        discard;
    }
}
