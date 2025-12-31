#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec4 v_color;
out vec2 v_uv;
out vec3 xyz_coords;

#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

uniform vec3 camera_position;
uniform float time;
uniform float brightness = 1.5;

void main() {
    xyz_coords = point;
    v_color = rgba;
    
    // UV coordinates using du_point and dv_point for proper ManimGL compatibility
    v_uv = vec2(0.5) + 0.5 * vec2(dot(normalize(du_point), vec3(1,0,0)), dot(normalize(dv_point), vec3(0,1,0)));
    
    emit_gl_Position(point);
}
