#version 330

// 输入属性：曲线点数据
in vec3 point;
in vec4 rgba;
in float glow_width;
in vec3 tangent;

// 输出到几何着色器的变量
out vec3 v_point;
out vec4 v_rgba;
out float v_glow_width;
out vec3 v_tangent;

void main(){
    v_point = point;
    v_rgba = rgba;
    v_glow_width = glow_width;
    v_tangent = tangent;
}
