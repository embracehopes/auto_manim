#version 330

// 输入属性：轨迹点数据
in vec3 point;
in vec4 rgba;
in float tail_progress;
in float tail_width;
in float glow_intensity;
in vec3 prev_dir;
in vec3 next_dir;

// 输出到几何着色器的变量
out vec3 v_point;
out vec4 v_rgba;
out float v_tail_progress;
out float v_tail_width;
out float v_glow_intensity;
out vec3 v_prev_dir;
out vec3 v_next_dir;

void main(){
    v_point = point;
    v_rgba = rgba;
    v_tail_progress = tail_progress;
    v_tail_width = tail_width;
    v_glow_intensity = glow_intensity;
    v_prev_dir = prev_dir;
    v_next_dir = next_dir;
    
    // 基础顶点位置变换
    gl_Position = vec4(point, 1.0);
}
