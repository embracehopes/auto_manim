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

void main() {
    // 设置顶点位置
    emit_gl_Position(point);
    
    // 计算简单的法向量
    vec3 du = du_point - point;
    vec3 dv = dv_point - point;
    vec3 normal = normalize(cross(du, dv));
    
    // 设置颜色
    v_color = rgba * brightness;
}
