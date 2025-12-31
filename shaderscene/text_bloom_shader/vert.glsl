#version 330

/*
 * 文字辉光顶点着色器
 * 直接传递顶点属性到几何着色器
 */

in vec3 point;
in vec4 rgba;
in float glow_radius;

out vec3 v_point;
out vec4 v_rgba;
out float v_glow_radius;

void main(){
    v_point = point;
    v_rgba = rgba;
    v_glow_radius = glow_radius;
}
