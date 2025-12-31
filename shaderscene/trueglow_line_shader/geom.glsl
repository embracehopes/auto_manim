#version 330

layout (lines) in;
layout (triangle_strip, max_vertices = 20) out;

uniform float pixel_size;
uniform float anti_alias_width;
uniform float frame_scale;
uniform vec3 camera_position;

in vec3 v_point[2];
in vec4 v_rgba[2];
in float v_glow_width[2];

out vec4 color;
out float scaled_aaw;
out vec3 point;
out vec3 to_cam;
out vec3 line_center;
out float glow_width;
out vec2 uv_coords;
out float line_length;
out vec3 line_start;
out vec3 line_end;
out float distance_to_line;

#INSERT emit_gl_Position.glsl

void main(){
    // 获取线段的两个端点
    vec3 p1 = v_point[0];
    vec3 p2 = v_point[1];
    
    // 计算线段参数
    vec3 line_vector = p2 - p1;
    line_length = length(line_vector);
    line_center = (p1 + p2) * 0.5;
    line_start = p1;
    line_end = p2;
    
    // 避免零长度线段
    if(line_length < 0.001) return;
    
    vec3 line_dir = normalize(line_vector);
    
    // 计算垂直于线段的两个正交方向
    to_cam = normalize(camera_position - line_center);
    vec3 line_normal = normalize(cross(line_dir, to_cam));
    vec3 line_binormal = normalize(cross(line_dir, line_normal));
    
    // 如果法线计算失败，使用默认方向
    if(length(line_normal) < 0.1){
        line_normal = vec3(0.0, 1.0, 0.0);
        line_binormal = vec3(0.0, 0.0, 1.0);
    }
    
    // 计算线条宽度
    float avg_glow_width = (v_glow_width[0] + v_glow_width[1]) * 0.5;
    glow_width = avg_glow_width;
    
    // 计算反锯齿缩放
    scaled_aaw = (anti_alias_width * pixel_size) / avg_glow_width;
    
    // 计算颜色插值
    vec4 avg_color = (v_rgba[0] + v_rgba[1]) * 0.5;
    color = avg_color;
    
    // 扩展线段以包含端点辉光
    float extend_length = avg_glow_width * 0.8;
    vec3 extended_p1 = p1 - line_dir * extend_length;
    vec3 extended_p2 = p2 + line_dir * extend_length;
    
    // 创建圆柱体辉光效果 - 使用4个方向近似圆形
    vec3 directions[4];
    directions[0] = line_normal;
    directions[1] = line_binormal;
    directions[2] = -line_normal;
    directions[3] = -line_binormal;
    
    // 生成主要的辉光条带
    for(int dir = 0; dir < 4; dir++) {
        vec3 radial_dir = directions[dir];
        
        // 为每个方向生成一个条带
        for(int i = 0; i < 2; i++) {
            vec3 base_point = (i == 0) ? extended_p1 : extended_p2;
            float t = float(i);
            
            // 中心轴顶点（从这里开始散发辉光）
            point = base_point;
            uv_coords = vec2(t, 0.0);
            distance_to_line = 0.0;
            emit_gl_Position(point);
            EmitVertex();
            
            // 外层辉光顶点
            point = base_point + radial_dir * avg_glow_width;
            uv_coords = vec2(t, 1.0);
            distance_to_line = avg_glow_width;
            emit_gl_Position(point);
            EmitVertex();
        }
        
        EndPrimitive();
    }
    
    // 添加端点的圆形辉光
    for(int end_idx = 0; end_idx < 2; end_idx++) {
        vec3 end_point = (end_idx == 0) ? p1 : p2;
        
        // 为端点创建圆形辉光
        for(int dir = 0; dir < 4; dir++) {
            vec3 radial_dir = directions[dir];
            
            // 端点中心
            point = end_point;
            uv_coords = vec2(float(end_idx), 0.0);
            distance_to_line = 0.0;
            emit_gl_Position(point);
            EmitVertex();
            
            // 端点外围
            point = end_point + radial_dir * avg_glow_width;
            uv_coords = vec2(float(end_idx), 1.0);
            distance_to_line = avg_glow_width;
            emit_gl_Position(point);
            EmitVertex();
            
            EndPrimitive();
        }
    }
}
