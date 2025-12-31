#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec4 v_color;
out vec3 v_position;  // 传递球面位置
#INSERT emit_gl_Position.glsl

uniform vec3 camera_position;
uniform float time;
uniform float brightness = 1.5;

const float EPSILON = 1e-10;

vec4 finalize_color(vec4 color, vec3 point, vec3 unit_normal){
    // 基本的光照和最终颜色处理
    vec3 n = normalize(unit_normal);
    vec3 to_camera = normalize(camera_position - point);
    
    float light = dot(n, normalize(vec3(1, 1, 1))) * 0.5 + 0.5;
    color.rgb *= light;
    
    return color;
}

void main(){
    // 设置位置
    emit_gl_Position(point);
    
    // 计算导数
    vec3 du = du_point - point;
    vec3 dv = dv_point - point;
    
    // 计算法向量
    vec3 normal = cross(du, dv);
    float normal_mag = length(normal);
    
    vec3 unit_normal = (normal_mag < EPSILON) ?
        normalize(point) : normalize(normal);
    
    // 传递归一化的球面位置给片段着色器
    v_position = normalize(point);
    
    // 最终颜色
    v_color = finalize_color(rgba, point, unit_normal);
}
