#version 330

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;

out vec3 v_point;
out vec3 v_du_point;
out vec3 v_dv_point;
out vec4 v_color;

#INSERT emit_gl_Position.glsl

void main() {
    v_point = point;
    v_du_point = du_point;
    v_dv_point = dv_point;
    v_color = rgba;
    emit_gl_Position(point);
}
