#version 330

layout (lines) in;
layout (triangle_strip, max_vertices = 12) out;

uniform float pixel_size;
uniform float anti_alias_width;
uniform float frame_scale;
uniform vec3 camera_position;
uniform mat4 perspective;

in vec3 v_point[2];
in vec4 v_rgba[2];
in float v_glow_width[2];
in vec3 v_tangent[2];

out vec4 color;
out float scaled_aaw;
out vec3 point;
out vec3 to_cam;
out vec3 curve_center;
out float glow_width;
out vec2 uv_coords;
out float curve_segment_length;
out vec3 tangent_dir;
out float distance_to_curve;

#INSERT emit_gl_Position.glsl

/*
 * 优化后的几何着色器
 * 
 * 核心改进：
 * 1. 使用屏幕空间计算法线方向，确保曲线宽度在任何角度都一致
 * 2. 简化几何结构，使用单个四边形条带
 * 3. 正确处理端点连接
 */

void main(){
    // 获取曲线段的两个端点
    vec3 p1 = v_point[0];
    vec3 p2 = v_point[1];
    
    // 计算曲线段参数
    vec3 segment_vector = p2 - p1;
    curve_segment_length = length(segment_vector);
    curve_center = (p1 + p2) * 0.5;
    
    // 避免零长度段
    if(curve_segment_length < 0.0001) return;
    
    vec3 segment_dir = normalize(segment_vector);
    
    // 使用切线方向
    vec3 tangent1 = length(v_tangent[0]) > 0.1 ? normalize(v_tangent[0]) : segment_dir;
    vec3 tangent2 = length(v_tangent[1]) > 0.1 ? normalize(v_tangent[1]) : segment_dir;
    tangent_dir = normalize(tangent1 + tangent2);
    
    // 计算相机方向
    to_cam = normalize(camera_position - curve_center);
    
    // 关键改进：计算屏幕空间的法线方向
    // 法线应该垂直于切线，且在屏幕平面内
    // 这样可以确保曲线在任何角度看起来宽度一致
    vec3 curve_normal = normalize(cross(tangent_dir, to_cam));
    
    // 如果切线和相机方向几乎平行，使用备用方向
    if(length(curve_normal) < 0.1){
        vec3 up = vec3(0.0, 1.0, 0.0);
        curve_normal = normalize(cross(tangent_dir, up));
        if(length(curve_normal) < 0.1){
            curve_normal = normalize(cross(tangent_dir, vec3(1.0, 0.0, 0.0)));
        }
    }
    
    // 计算每个端点的法线方向（确保平滑连接）
    vec3 normal1 = normalize(cross(tangent1, to_cam));
    vec3 normal2 = normalize(cross(tangent2, to_cam));
    if(length(normal1) < 0.1) normal1 = curve_normal;
    if(length(normal2) < 0.1) normal2 = curve_normal;
    
    // 计算曲线宽度
    float gw1 = v_glow_width[0];
    float gw2 = v_glow_width[1];
    float avg_glow_width = (gw1 + gw2) * 0.5;
    glow_width = avg_glow_width;
    
    // 计算反锯齿缩放
    scaled_aaw = (anti_alias_width * pixel_size) / max(avg_glow_width, 0.001);
    
    // 颜色
    vec4 color1 = v_rgba[0];
    vec4 color2 = v_rgba[1];
    
    // 生成四边形条带（两个三角形）
    // 结构：上边 -> 下边，从 p1 到 p2
    //
    //  p1_top -------- p2_top
    //    |               |
    //  p1     -------- p2
    //    |               |
    //  p1_bot -------- p2_bot
    
    vec3 offset1 = normal1 * gw1;
    vec3 offset2 = normal2 * gw2;
    
    // 顶点1：p1上方
    point = p1 + offset1;
    color = color1;
    uv_coords = vec2(0.0, 1.0);  // y=1 表示在边缘
    distance_to_curve = gw1;
    emit_gl_Position(point);
    EmitVertex();
    
    // 顶点2：p1下方
    point = p1 - offset1;
    color = color1;
    uv_coords = vec2(0.0, -1.0);  // y=-1 表示在另一边缘
    distance_to_curve = gw1;
    emit_gl_Position(point);
    EmitVertex();
    
    // 顶点3：p2上方
    point = p2 + offset2;
    color = color2;
    uv_coords = vec2(1.0, 1.0);
    distance_to_curve = gw2;
    emit_gl_Position(point);
    EmitVertex();
    
    // 顶点4：p2下方
    point = p2 - offset2;
    color = color2;
    uv_coords = vec2(1.0, -1.0);
    distance_to_curve = gw2;
    emit_gl_Position(point);
    EmitVertex();
    
    EndPrimitive();
}
