#version 330

uniform float glow_factor;
uniform float core_width_ratio;
uniform float anti_alias_width;
uniform mat4 perspective;

in vec4 color;
in float scaled_aaw;
in vec3 point;
in vec3 to_cam;
in vec3 line_center;
in float glow_width;
in vec2 uv_coords;
in float line_length;

out vec4 frag_color;

// This include a delaration of uniform vec3 shading
#INSERT finalize_color.glsl

void main() {
    // 计算到线条中心轴的归一化距离
    float r = abs(uv_coords.y);
    
    // 如果超出边界则丢弃
    if(r > 1.0) discard;

    frag_color = color;

    // 应用改进的辉光效果：从中心轴开始散发
    if(glow_factor > 0){
        // 使用 true_dot 风格的幂函数衰减，从中心轴(r=0)开始
        float glow_alpha = pow(1.0 - r, glow_factor);
        
        // 核心线条区域（中心附近）保持更高的亮度
        float core_intensity = 1.0;
        if(r <= core_width_ratio){
            core_intensity = 1.2 + (1.0 - r / core_width_ratio) * 0.3;
        } else {
            core_intensity = 1.0 + glow_factor * 0.3 * (1.0 - r);
        }
        
        // 应用亮度增强，保持原始颜色
        frag_color.rgb *= core_intensity;
        
        // 应用辉光透明度衰减
        frag_color.a *= glow_alpha;
    }

    // 应用着色（如果启用）
    if(shading != vec3(0.0)){
        // 对于线条，我们使用一个简化的法线计算
        vec3 line_normal = normalize(cross(normalize(point - line_center), to_cam));
        frag_color = finalize_color(frag_color, point, line_normal);
    }

    // 应用反锯齿
    frag_color.a *= smoothstep(1.0, 1.0 - scaled_aaw, r);
}
