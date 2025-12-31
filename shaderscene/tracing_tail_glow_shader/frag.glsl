#version 330

uniform float glow_factor;
uniform float anti_alias_width;
uniform float tail_lifetime;
uniform mat4 perspective;

// ===== 可调试参数接口 =====
// 这些参数可以从 Python 代码中传入，实现实时调整效果

// 颜色与亮度控制
uniform float color_saturation = 2.0;      // 颜色饱和度 (0.0-2.0, 默认1.0)
uniform float brightness_multiplier = 2.0; // 整体亮度倍数 (0.5-2.0, 默认1.0)
uniform float core_brightness =4.0;       // 核心亮度 (1.0-3.0, 默认1.8)
uniform float max_color_clamp = 1.5;       // 最大颜色限制 (1.0-2.5, 默认1.5)

// 辉光形状控制
uniform float glow_width = 5.0;            // 辉光宽度倍数 (0.5-2.0, 默认1.0)
uniform float glow_blur = 3.0;             // 辉光模糊度/衰减系数 (0.8-3.0, 默认1.5)
uniform float core_radius = 0.15;          // 核心区域半径 (0.05-0.3, 默认0.15)
uniform float edge_softness = 5.0;         // 边缘柔化程度 (1.0-5.0, 默认3.0)

// 透明度控制
uniform float alpha_base = 0.8;            // 基础透明度 (0.5-1.0, 默认0.8)
uniform float alpha_core_boost = 1.1;      // 核心透明度增强 (1.0-1.5, 默认1.1)

// 轨迹头部效果
uniform float head_boost_strength = 0.1;  // 头部增强强度 (0.0-0.5, 默认0.25)
uniform float head_boost_range = 0.1;      // 头部增强范围 (0.05-0.2, 默认0.1)

in vec4 color;
in float scaled_aaw;
in vec3 point;
in vec3 to_cam;
in vec2 uv_coords;
in float tail_progress;
in float glow_intensity;
in float distance_to_center;

out vec4 frag_color;

// This include a declaration of uniform vec3 shading
#INSERT finalize_color.glsl

void main() {
    // 计算到轨迹中心线的归一化距离
    float r = abs(uv_coords.y);
    float radial = clamp(r / 5.0, 0.0, 1.0);
    
    // 超出边界则丢弃
    if(r > 5.0) discard;

    frag_color = color;
    
    // 应用颜色饱和度调整
    vec3 gray = vec3(dot(frag_color.rgb, vec3(0.299, 0.587, 0.114)));
    frag_color.rgb = mix(gray, frag_color.rgb, color_saturation);

    // === 电影级别的轨迹辉光效果 ===
    
    // 1. 基础辉光衰减 - 使用可调节的模糊度参数
    float falloff_strength = max(glow_factor * 0.85, 0.45);
    float base_glow = pow(1.0 - radial, falloff_strength);
    base_glow = mix(base_glow, exp(-radial * glow_blur), 0.4);  // 使用 glow_blur 参数
    
    // 2. 轨迹年龄衰减 - 越老的轨迹越透明
    float age_fade = 1.0 - pow(tail_progress, 1.6);  // 略微减缓衰减，维持亮度
    
    // 3. 核心亮度增强 - 使用可调节的核心半径和亮度参数
    float inner_mix = smoothstep(0.0, core_radius, radial);          // 使用 core_radius 参数
    float mid_mix = smoothstep(core_radius, 0.5 * glow_width, radial);
    float outer_mix = smoothstep(0.5 * glow_width, 1.0, radial);

    float inner_peak = core_brightness - inner_mix * 0.2;  // 使用 core_brightness 参数
    float mid_peak = 1.25 + glow_intensity * 0.2 * (1.0 - radial);
    float outer_peak = 0.9 + glow_intensity * 0.15 * (1.0 - radial);

    float core_intensity = mix(inner_peak, mid_peak, mid_mix);
    core_intensity = mix(core_intensity, outer_peak, outer_mix);
    
    // 4. 动态辉光强度调整 - 适度增强，避免颜色失真
    float dynamic_glow = glow_intensity * (0.75 + 0.2 * (1.0 - radial)) * age_fade;
    
    // 5. 应用所有效果 - 使用可调节的亮度倍数
    float brightness_boost = brightness_multiplier * (1.0 + dynamic_glow * 0.22);
    if(radial < core_radius) {
        brightness_boost *= 1.15;
    }
    frag_color.rgb *= core_intensity * brightness_boost;
    
    // 透明度组合：使用可调节的透明度参数
    float final_alpha = base_glow * age_fade * (alpha_base + dynamic_glow * 0.25);
    if(radial < core_radius) {
        final_alpha *= alpha_core_boost;  // 使用 alpha_core_boost 参数
    }
    frag_color.a *= final_alpha;
    
    // 6. 特殊效果：轨迹头部增强 - 使用可调节的头部增强参数
    if(tail_progress < head_boost_range) {
        float head_boost = (1.0 - tail_progress / head_boost_range) * head_boost_strength;
        if(radial < 0.3) {
            head_boost *= 1.3;
        }
        frag_color.rgb *= (1.0 + head_boost);
        frag_color.a *= (1.0 + head_boost * 0.35);
    }
    
    // 7. 轨迹末端柔化
    if(tail_progress > 0.8) {
        // 轨迹的最老部分（20%）柔化处理
        float tail_softness = (tail_progress - 0.8) / 0.2;
        frag_color.a *= (1.0 - tail_softness * 0.3);
    }

    // 应用着色（如果启用）
    if(shading != vec3(0.0)){
        // 为轨迹使用简化的法线计算
        vec3 trail_normal = normalize(cross(to_cam, vec3(0, 0, 1)));
        frag_color = finalize_color(frag_color, point, trail_normal);
    }

    // 应用反锯齿 - 使用可调节的边缘柔化参数
    float aa_factor = smoothstep(1.0, 1.0 - scaled_aaw * edge_softness, r);
    frag_color.a *= aa_factor;
    
    // 最终颜色限制 - 使用可调节的最大亮度限制
    frag_color.rgb = min(frag_color.rgb, vec3(max_color_clamp));
    
    // 额外的颜色保护：如果颜色过亮，保留色相
    float max_rgb = max(max(frag_color.r, frag_color.g), frag_color.b);
    float safe_threshold = max_color_clamp * 0.87;  // 动态阈值
    if(max_rgb > safe_threshold) {
        vec3 normalized_color = frag_color.rgb / max_rgb;
        frag_color.rgb = normalized_color * safe_threshold;
    }
    
    // 确保透明度在有效范围内
    frag_color.a = clamp(frag_color.a, 0.0, 1.0);
    
    // === 智能discard：只丢弃真正不可见的像素 ===
    
    // 计算颜色的亮度（luminance）
    float luminance = dot(frag_color.rgb, vec3(0.299, 0.587, 0.114));
    
    // 多重判断条件来识别"真正不可见"的像素
    bool is_invisible = false;
    
    // 条件1：透明度极低（几乎完全透明）
    if(frag_color.a < 0.01) {
        is_invisible = true;
    }
    
    // 条件2：结合亮度和透明度的综合判断（可见度极低）
    float visibility = luminance * frag_color.a;
    if(visibility < 0.005) {  // 降低阈值，只丢弃真正看不见的
        is_invisible = true;
    }
    
    // 条件3：轨迹尾部的极端暗色区域
    if(tail_progress > 0.95 && visibility < 0.01) {
        is_invisible = true;
    }
    
    // 执行discard（只丢弃真正不可见的像素）
    if(is_invisible) {
        discard;
    }

    if(r > 0.92) {
        float edge_luminance = dot(frag_color.rgb, vec3(0.299, 0.587, 0.114));
        if(frag_color.a < 0.08 && edge_luminance < 0.15) {
            discard;
        }
    }
}
