#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec4 v_color;
#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

uniform vec3 camera_position;
uniform float time;
uniform float brightness = 1.5;

const float PI = 3.14159265359;
const float TAU = 6.28318530718;
const float PHI = 1.618033988749;
const float EPSILON = 1e-10;

// 预计算的20面体顶点
const vec3 ico_verts[12] = vec3[12](
    vec3(0.0, 0.525731, 0.850651),
    vec3(0.0, -0.525731, 0.850651),
    vec3(0.0, 0.525731, -0.850651),
    vec3(0.0, -0.525731, -0.850651),
    vec3(0.525731, 0.850651, 0.0),
    vec3(-0.525731, 0.850651, 0.0),
    vec3(0.525731, -0.850651, 0.0),
    vec3(-0.525731, -0.850651, 0.0),
    vec3(0.850651, 0.0, 0.525731),
    vec3(-0.850651, 0.0, 0.525731),
    vec3(0.850651, 0.0, -0.525731),
    vec3(-0.850651, 0.0, -0.525731)
);

// 调色板函数
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(TAU * (c * t + d));
}

// 光谱颜色
vec3 spectrum_color(float t) {
    return palette(t,
        vec3(0.5, 0.5, 0.5),
        vec3(0.5, 0.5, 0.5),
        vec3(1.0, 1.0, 1.0),
        vec3(0.0, 0.33, 0.67)
    );
}

// 测地线颜色
vec3 geodesic_color(float t) {
    return palette(t,
        vec3(0.3, 0.4, 0.8),
        vec3(0.6, 0.3, 0.4),
        vec3(2.0, 1.5, 1.0),
        vec3(0.0, 0.2, 0.5)
    );
}

// 20面体域镜像
vec3 icosahedron_mirror(vec3 p) {
    vec3 result = normalize(p);
    
    for (int i = 0; i < 3; i++) {
        float max_dot = -1.0;
        int closest = 0;
        
        for (int j = 0; j < 12; j++) {
            float d = dot(result, ico_verts[j]);
            if (d > max_dot) {
                max_dot = d;
                closest = j;
            }
        }
        
        vec3 axis = ico_verts[closest];
        result = reflect(result, axis);
        result = normalize(result);
    }
    
    return result;
}

// 测地线模式
float geodesic_pattern(vec3 p) {
    vec3 mirrored = icosahedron_mirror(p);
    
    float u = atan(mirrored.y, mirrored.x) / TAU + 0.5;
    float v = acos(clamp(mirrored.z, -1.0, 1.0)) / PI;
    
    float scale = 10.0 + 6.0 * sin(time * 0.6);
    vec2 grid = vec2(u, v) * scale;
    
    grid.x *= 0.866025;
    vec2 id = floor(grid);
    vec2 local = fract(grid);
    
    if (mod(id.y, 2.0) == 1.0) {
        local.x += 0.5;
        id.x = floor(grid.x + 0.5);
    }
    
    local = fract(local);
    float dist = length(local - vec2(0.5));
    
    float edge_thickness = 0.06 + 0.03 * sin(time * 1.5);
    return smoothstep(0.4 - edge_thickness, 0.4, dist);
}

// 边缘检测
float edge_detection(vec3 p, vec3 normal) {
    float geodesic_edge = geodesic_pattern(p);
    
    vec3 n = normalize(normal);
    vec3 world_pos = p;
    float delta = 0.02;
    
    vec3 dx = normalize(world_pos + vec3(delta, 0.0, 0.0));
    vec3 dy = normalize(world_pos + vec3(0.0, delta, 0.0));
    
    float edge_factor = length(dx - normalize(world_pos)) + 
                       length(dy - normalize(world_pos));
    edge_factor = smoothstep(0.01, 0.05, edge_factor);
    
    return max(geodesic_edge, edge_factor);
}

// 动态位置变换
vec3 animate_position(vec3 p) {
    vec3 mirrored = icosahedron_mirror(p);
    
    float wave1 = sin(time * 1.2 + dot(mirrored, vec3(2.0, 3.0, 1.0))) * 0.03;
    float wave2 = cos(time * 1.8 + length(mirrored.xy) * 6.0) * 0.02;
    float wave3 = sin(time * 0.9 + mirrored.z * 4.0) * 0.025;
    
    vec3 displacement = normalize(p) * (wave1 + wave2 + wave3);
    
    return p + displacement;
}

// 最终颜色计算
vec4 finalize_color(vec4 base_color, vec3 world_pos, vec3 unit_normal) {
    vec3 n = normalize(unit_normal);
    vec3 to_camera = normalize(camera_position - world_pos);
    
    // Fresnel效果
    float fresnel = 1.0 - abs(dot(n, to_camera));
    fresnel = pow(fresnel, 1.2);
    
    // 测地线模式
    float geodesic_value = geodesic_pattern(normalize(world_pos));
    vec3 geodesic_col = geodesic_color(geodesic_value + time * 0.25);
    
    // 20面体域颜色
    vec3 mirrored = icosahedron_mirror(normalize(world_pos));
    float domain_factor = dot(mirrored, vec3(1.0, 1.0, 1.0)) * 0.5 + 0.5;
    vec3 spectrum_col = spectrum_color(domain_factor + time * 0.15);
    
    // 边缘检测
    float edge_highlight = edge_detection(world_pos, n);
    vec3 edge_color = vec3(1.0, 0.7, 0.2);
    
    // 颜色混合
    float time_wave = sin(time * 1.0) * 0.5 + 0.5;
    vec3 final_color = mix(geodesic_col, spectrum_col, time_wave);
    
    // 边缘高亮
    final_color = mix(final_color, edge_color, edge_highlight * 0.6);
    
    // Fresnel发光
    vec3 fresnel_color = vec3(0.3, 0.7, 1.0);
    final_color += fresnel_color * fresnel * 0.4;
    
    // 距离衰减
    float depth = length(world_pos - camera_position);
    float distance_fade = 1.0 / (1.0 + depth * 0.03);
    final_color *= distance_fade;
    
    // 动态亮度
    float pulse = 0.75 + 0.25 * sin(time * 2.0 + domain_factor * 8.0);
    final_color *= pulse;
    
    // 亮度调节
    final_color = pow(final_color, vec3(0.9)) * brightness;
    
    float alpha = 0.88 + 0.12 * fresnel;
    
    return vec4(final_color, alpha);
}

void main() {
    // 动态位置
    vec3 animated_pos = animate_position(point);
    
    // 设置位置
    emit_gl_Position(animated_pos);
    
    // 计算导数
    vec3 du = animate_position(du_point) - animated_pos;
    vec3 dv = animate_position(dv_point) - animated_pos;
    
    // 法向量
    vec3 normal = cross(du, dv);
    float normal_mag = length(normal);
    
    vec3 unit_normal = (normal_mag < EPSILON) ?
        normalize(animated_pos) : normalize(normal);
    
    // 最终颜色
    v_color = finalize_color(rgba, animated_pos, unit_normal);
}
