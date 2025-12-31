#version 330

in vec4 v_color;
out vec4 frag_color;

uniform float time;
uniform float brightness = 1.5;
uniform vec2 resolution = vec2(800.0, 600.0);

// Tanh function for tonemapping
vec4 tanh_tonemap(vec4 color) {
    return tanh(color / 2000.0);
}

void main() {
    vec2 I = gl_FragCoord.xy;
    vec2 iResolution = resolution;
    float iTime = time;
    vec4 O = vec4(0.0);
    
    // Time for waves and coloring
    float t = iTime;
    // Raymarch iterator
    float i = 0.0;
    // Raymarch depth
    float z = 0.0;
    // Raymarch step distance
    float d = 0.0;
    // Signed distance for coloring
    float s = 0.0;
    
    // Clear fragcolor and raymarch loop 100 times
    for (O *= i; i < 100.0; i++) {
        // Raymarch sample point
        vec3 p = z * normalize(vec3(I + I, 0.0) - iResolution.xyy);
        // Vector for undistorted coordinates
        vec3 v;
        
        // Shift camera back 9 units
        p.z += 9.0;
        
        // Save coordinates
        v = p;
        
        // Apply turbulence waves
        // https://mini.gmshaders.com/p/turbulence
        for (d = 1.0; d < 9.0; d += d) {
            p += 0.5 * sin(p.yzx * d + t) / d;
        }
        
        // Distance to gyroid
        z += d = 0.2 * (0.01 + abs(s = dot(cos(p), sin(p / 0.7).yzx))
        // Spherical boundary
        - min(d = 6.0 - length(v), -d * 0.1));
        
        // Coloring and glow attenuation
        O += (cos(s / 0.1 + z + t + vec4(2.0, 4.0, 5.0, 0.0)) + 1.2) / d / z;
    }
    
    // Tanh tonemapping
    // https://www.shadertoy.com/view/ms3BD7
    O = tanh_tonemap(O);
    
    // Apply brightness and output
    frag_color = O * brightness;
}
