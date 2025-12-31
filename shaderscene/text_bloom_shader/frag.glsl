#version 330

/*
 * 文字辉光片段着色器 - 高级 Bloom 效果
 * 
 * 实现高质量的柔和白色辉光效果：
 * 1. 使用多重高斯采样实现平滑模糊
 * 2. 白色核心 + 柔和扩散的辉光边缘
 * 3. 可调节的辉光强度和衰减
 */

uniform float glow_intensity;      // 辉光强度 (0.5 - 2.0)
uniform float glow_softness;       // 辉光柔和度 (0.3 - 0.8)
uniform float white_core_strength; // 白色核心强度 (0.2 - 0.6)
uniform float falloff_power;       // 衰减指数 (1.0 - 3.0)

in vec4 color;
in vec2 uv;
in float scaled_aaw;
in float glow_size;

out vec4 frag_color;

#INSERT finalize_color.glsl

/*
 * 高斯函数 - 生成平滑的钟形曲线
 */
float gaussian(float x, float sigma) {
    float s = max(sigma, 0.001);
    return exp(-0.5 * (x * x) / (s * s));
}

/*
 * 平滑的三次 Hermite 插值
 */
float smootherstep(float edge0, float edge1, float x) {
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0);
}

/*
 * 多层高斯模糊采样 - 在shader中实现真正的模糊效果
 */
float multi_gaussian_blur(float r, float softness) {
    // 使用多个sigma值叠加实现更柔和的效果
    float blur = 0.0;
    float sigma1 = softness * 0.3;
    float sigma2 = softness * 0.6;
    float sigma3 = softness * 1.0;
    
    blur += gaussian(r, sigma1) * 0.5;
    blur += gaussian(r, sigma2) * 0.35;
    blur += gaussian(r, sigma3) * 0.15;
    
    return blur;
}

void main() {
    // 计算到中心的归一化距离 [0, 1]
    float r = length(uv);
    
    // 超出辉光范围则丢弃
    if (r > 1.0) {
        discard;
    }
    
    // === 辉光计算 ===
    
    // 1. 多层高斯模糊实现柔和边缘
    float blur_value = multi_gaussian_blur(r, glow_softness);
    
    // 2. 白色核心 - 中心最亮，使用陡峭的高斯
    float white_core = gaussian(r, white_core_strength * 0.25);
    white_core = pow(white_core, 0.7); // 增强核心对比度
    
    // 3. 辉光衰减 - 边缘逐渐变淡
    float falloff = pow(1.0 - r, falloff_power);
    
    // === 颜色混合 ===
    
    // 基础颜色（传入的颜色，通常是白色）
    vec3 base_color = color.rgb;
    vec3 white = vec3(1.0);
    
    // 核心区域：纯白色渐变到基础色
    float core_blend = smootherstep(0.0, 0.3, r);
    vec3 mixed_color = mix(white, base_color, core_blend);
    
    // 增强中心亮度
    float brightness = 1.0 + (1.0 - core_blend) * 0.3 * glow_intensity;
    mixed_color *= brightness;
    
    // === 透明度计算 ===
    
    // 组合blur和核心，乘以衰减
    float alpha_base = blur_value * 0.6 + white_core * 0.4;
    float final_alpha = alpha_base * falloff * color.a * glow_intensity;
    
    // 平滑alpha曲线
    final_alpha = smoothstep(0.0, 1.0, final_alpha);
    
    // 边缘抗锯齿
    float edge_aa = smoothstep(1.0, 1.0 - scaled_aaw * 2.0, r);
    final_alpha *= edge_aa;
    
    // 输出
    frag_color = vec4(mixed_color, final_alpha);
    frag_color = finalize_color(frag_color, vec3(0.0), vec3(0.0));
    
    // 丢弃完全透明的像素
    if (frag_color.a <= 0.002) {
        discard;
    }
}
