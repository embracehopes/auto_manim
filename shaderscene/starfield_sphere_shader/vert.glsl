#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec3 v_position;
out vec2 v_uv;
out vec4 v_color;

// 新增：球体中心 uniform，用于位置无关性
uniform vec3 sphere_center;

// 插入标准函数定义
#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

uniform vec3 camera_position;
uniform float time;
uniform float brightness = 1.5;

const float PI = 3.14159265359;

void main(){
    // 使用本地坐标计算位置无关的纹理坐标
    vec3 local_position = point - sphere_center;
    v_position = normalize(local_position);

    // 计算球面 UV 坐标
    // 将 3D 球面坐标转换为 2D UV 坐标
    float phi = atan(v_position.z, v_position.x);
    float theta = acos(v_position.y);

    // 归一化到 [0, 1] 范围
    v_uv = vec2(
        (phi + PI) / (2.0 * PI),
        theta / PI
    );

    // 设置位置
    emit_gl_Position(point);

    // 计算导数用于法线
    vec3 du = du_point - point;
    vec3 dv = dv_point - point;

    // 法向量
    vec3 normal = cross(du, dv);
    vec3 unit_normal = get_unit_normal(point, du_point, dv_point);

    // 基础颜色（星星效果将在片段着色器中计算）
    v_color = rgba * brightness;
}
