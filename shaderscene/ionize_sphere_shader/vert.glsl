#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec4 v_color;
out vec3 world_position;  // 传递世界坐标到片段着色器
#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

uniform vec3 camera_position;
uniform vec3 sphere_center;
uniform float time;
uniform float brightness = 1.5;

void main() {
    // 设置顶点位置
    emit_gl_Position(point);
    
    // 传递世界坐标给片段着色器
    
    
    // 计算简单的法向量
    vec3 du = du_point - point;
    vec3 dv = dv_point - point;
    vec3 normal = normalize(cross(du, dv));
    world_position = point;
    


    // 设置颜色
    v_color = rgba * brightness;
}
