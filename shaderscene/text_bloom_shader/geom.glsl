#version 330

/*
 * 文字辉光几何着色器
 * 将每个点扩展为辉光四边形
 */

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform vec3 camera_position;
uniform float anti_alias_width;
uniform float pixel_size;

in vec3 v_point[1];
in vec4 v_rgba[1];
in float v_glow_radius[1];

out vec4 color;
out vec2 uv;
out float scaled_aaw;
out float glow_size;

#INSERT emit_gl_Position.glsl

vec3 safe_cross(vec3 a, vec3 b){
    vec3 result = cross(a, b);
    if(length(result) < 1e-3){
        if(abs(a.y) < 0.9){
            result = cross(a, vec3(0.0, 1.0, 0.0));
        }else{
            result = cross(a, vec3(1.0, 0.0, 0.0));
        }
    }
    return normalize(result);
}

void main(){
    vec3 center = v_point[0];
    float radius = v_glow_radius[0];
    if(radius <= 0.0){
        radius = 0.05;
    }
    
    color = v_rgba[0];
    glow_size = radius;
    scaled_aaw = anti_alias_width * pixel_size / max(radius, 0.001);

    vec3 to_cam = normalize(camera_position - center);
    if(length(to_cam) < 0.001){
        to_cam = vec3(0.0, 0.0, 1.0);
    }

    vec3 right = safe_cross(to_cam, vec3(0.0, 1.0, 0.0));
    vec3 up = safe_cross(right, to_cam);

    vec2 corners[4] = vec2[4](
        vec2(-1.0, -1.0),
        vec2(1.0, -1.0),
        vec2(-1.0, 1.0),
        vec2(1.0, 1.0)
    );

    for(int i=0; i<4; i++){
        vec2 corner = corners[i];
        vec3 offset = right * corner.x + up * corner.y;
        uv = corner;
        emit_gl_Position(center + offset * radius);
        EmitVertex();
    }
    EndPrimitive();
}
