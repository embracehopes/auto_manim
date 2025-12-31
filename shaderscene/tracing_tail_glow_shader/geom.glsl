#version 330

layout (lines) in;
layout (triangle_strip, max_vertices = 8) out;

uniform float pixel_size;
uniform float anti_alias_width;
uniform float frame_scale;
uniform vec3 camera_position;
uniform float tail_lifetime;

in vec3 v_point[2];
in vec4 v_rgba[2];
in float v_tail_progress[2];
in float v_tail_width[2];
in float v_glow_intensity[2];
in vec3 v_prev_dir[2];
in vec3 v_next_dir[2];

out vec4 color;
out float scaled_aaw;
out vec3 point;
out vec3 to_cam;
out vec2 uv_coords;
out float tail_progress;
out float glow_intensity;
out float distance_to_center;

#INSERT emit_gl_Position.glsl

vec3 safe_normalize(vec3 v, vec3 fallback){
    float len_v = length(v);
    if(len_v < 1e-5){
        float len_fb = length(fallback);
        if(len_fb < 1e-5){
            return vec3(0.0, 1.0, 0.0);
        }
        return fallback / len_fb;
    }
    return v / len_v;
}

vec3 compute_offset(vec3 dir_in, vec3 dir_out, vec3 to_cam_dir, float width, vec3 reference_normal){
    vec3 normal_in = safe_normalize(cross(to_cam_dir, dir_in), reference_normal);
    vec3 normal_out = safe_normalize(cross(to_cam_dir, dir_out), normal_in);
    vec3 miter = normal_in + normal_out;

    if(length(miter) < 1e-5){
        miter = reference_normal;
    }

    miter = safe_normalize(miter, reference_normal);
    float denom = abs(dot(miter, normal_out));
    denom = max(denom, 0.25);
    float miter_length = width / denom;
    miter_length = min(miter_length, width * 4.0);
    return miter * miter_length;
}

void main(){
    vec3 p1 = v_point[0];
    vec3 p2 = v_point[1];

    vec3 segment_vec = p2 - p1;
    float segment_len = length(segment_vec);
    if(segment_len < 0.0001){
        return;
    }

    vec3 segment_dir = segment_vec / segment_len;

    float width1 = max(v_tail_width[0], 1e-5);
    float width2 = max(v_tail_width[1], 1e-5);
    float avg_width = 0.5 * (width1 + width2);

    vec3 to_cam1 = safe_normalize(camera_position - p1, vec3(0.0, 0.0, 1.0));
    vec3 to_cam2 = safe_normalize(camera_position - p2, to_cam1);

    vec3 dir_prev_start = safe_normalize(v_prev_dir[0], segment_dir);
    vec3 dir_next_start = safe_normalize(v_next_dir[0], segment_dir);
    vec3 dir_prev_end = safe_normalize(v_prev_dir[1], segment_dir);
    vec3 dir_next_end = safe_normalize(v_next_dir[1], segment_dir);

    vec3 reference_start = safe_normalize(cross(to_cam1, dir_next_start), safe_normalize(cross(to_cam1, segment_dir), vec3(0.0, 1.0, 0.0)));
    vec3 reference_end = safe_normalize(cross(to_cam2, dir_prev_end), safe_normalize(cross(to_cam2, segment_dir), reference_start));

    vec3 offset_start = compute_offset(dir_prev_start, dir_next_start, to_cam1, width1, reference_start);
    vec3 offset_end = compute_offset(dir_prev_end, dir_next_end, to_cam2, width2, reference_end);

    float offset_start_len = length(offset_start);
    float offset_end_len = length(offset_end);

    float aa_scale = (anti_alias_width * pixel_size) / max(avg_width, 0.001);

    vec3 strip_positions[4];
    strip_positions[0] = p1 + offset_start;
    strip_positions[1] = p1 - offset_start;
    strip_positions[2] = p2 + offset_end;
    strip_positions[3] = p2 - offset_end;

    vec2 uv_values[4];
    uv_values[0] = vec2(0.0, 1.0);
    uv_values[1] = vec2(0.0, -1.0);
    uv_values[2] = vec2(1.0, 1.0);
    uv_values[3] = vec2(1.0, -1.0);

    float distances[4];
    distances[0] = offset_start_len;
    distances[1] = offset_start_len;
    distances[2] = offset_end_len;
    distances[3] = offset_end_len;

    vec4 colors[4];
    colors[0] = v_rgba[0];
    colors[1] = v_rgba[0];
    colors[2] = v_rgba[1];
    colors[3] = v_rgba[1];

    float progresses[4];
    progresses[0] = v_tail_progress[0];
    progresses[1] = v_tail_progress[0];
    progresses[2] = v_tail_progress[1];
    progresses[3] = v_tail_progress[1];

    float intensities[4];
    intensities[0] = v_glow_intensity[0];
    intensities[1] = v_glow_intensity[0];
    intensities[2] = v_glow_intensity[1];
    intensities[3] = v_glow_intensity[1];

    vec3 to_cams[4];
    to_cams[0] = to_cam1;
    to_cams[1] = to_cam1;
    to_cams[2] = to_cam2;
    to_cams[3] = to_cam2;

    for(int i = 0; i < 4; ++i){
        point = strip_positions[i];
        color = colors[i];
        tail_progress = progresses[i];
        glow_intensity = intensities[i];
        uv_coords = uv_values[i];
        distance_to_center = distances[i];
        to_cam = to_cams[i];
        scaled_aaw = aa_scale;
        emit_gl_Position(point);
        EmitVertex();
    }

    EndPrimitive();
}
