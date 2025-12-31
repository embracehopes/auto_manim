#version 330

in vec4 v_color;
out vec4 frag_color;

uniform float time;

void main() {
    // 基础颜色来自顶点着色器
    vec4 base_color = v_color;
    
    // 添加细微的片段级效果
    vec2 screen_pos = gl_FragCoord.xy * 0.001;
    float noise = sin(screen_pos.x * 50.0 + time * 2.0) * 
                  cos(screen_pos.y * 50.0 + time * 1.5) * 0.01;
    
    // 轻微的颜色扰动

    
    // 确保颜色在合理范围内
    base_color.rgb = clamp(base_color.rgb, 0.0, 1.0);
    
    frag_color = base_color;
}
