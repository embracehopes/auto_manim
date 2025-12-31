#version 330

in vec4 v_color;
in vec3 world_position;  // 从顶点着色器接收世界坐标
out vec4 frag_color;

uniform float time;
uniform float brightness = 1.5;
uniform vec2 resolution = vec2(800.0, 600.0);
uniform vec3 sphere_center;  // 球心位置（绝对坐标）

// Tanh function for tonemapping
vec4 tanh_tonemap(vec4 color) {
    return tanh(color / 2000.0);
}

void main() {
    // 1. 完全使用本地坐标系 - 关键修复
    vec3 local_pos = world_position - sphere_center;
    
    // 2. 确保使用本地坐标系的射线方向
    vec3 ray_dir = normalize(local_pos);
    
    vec4 O = vec4(0.0);
    float t = time;
    float i = 0.0;
    float z = 0.0;
    float d = 0.0;
    float s = 0.0;
    
    // 3. 在本地坐标系中进行raymarch
    for (O *= i; i < 100.0; i++) {
        // 4. 完全基于本地坐标的采样点
        vec3 p = ray_dir * z;
        vec3 v = p;
        
        // 5. 波动效果 - 纯本地坐标
        for (d = 1.0; d < 9.0; d += d) {
            p += 0.5 * sin(p.yzx * d + t) / d;
        }
        
        // 6. 距离函数 - 纯本地坐标
        z += d = 0.2 * (0.01 + abs(s = dot(cos(p), sin(p / 0.7).yzx))
                      - min(d = 6.0 - length(v), -d * 0.1));
        
        // 着色
        O += (cos(s / 0.1 + z + t + vec4(2.0, 4.0, 5.0, 0.0)) + 1.2) / d / z;
    }
    
    O = tanh_tonemap(O);
    frag_color = O * brightness;
}