#version 330

in vec4 v_color;
in vec3 v_position;  // 从顶点着色器接收本地球面位置
out vec4 frag_color;

uniform vec3 camera_position;
uniform float time;
uniform float brightness = 1.5;
uniform vec3 sphere_center;  // 球体中心（用于调试，片段着色器中不直接使用）

// 常数定义
const float PI = 3.14159265359;

// 旋转矩阵函数
mat2 mm2(in float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}

vec3 rotx(vec3 p, float a) {
    float s = sin(a), c = cos(a);
    return vec3(p.x, c*p.y - s*p.z, s*p.y + c*p.z);
}

vec3 roty(vec3 p, float a) {
    float s = sin(a), c = cos(a);
    return vec3(c*p.x + s*p.z, p.y, -s*p.x + c*p.z);
}

vec3 rotz(vec3 p, float a) {
    float s = sin(a), c = cos(a);
    return vec3(c*p.x - s*p.y, s*p.x + c*p.y, p.z);
}

//---------------------------纹理函数--------------------------------
vec3 texpent(in vec2 p, in float idx) {   
    float siz = 1920.0 * 0.02;  // 增加尺寸因子
    p *= 0.6;  // 增加密度
    vec2 q = abs(p);
    float rz = sin(clamp(max(max(q.x*1.176-p.y*0.385, q.x*0.727+p.y),
                             -p.y*1.237)*15., 0., 25.))*siz+siz;
    vec3 col = (sin(vec3(1, 1.5, 5)*idx)+2.)*(rz+0.25);
    col -= sin(dot(p,p)*4.+time*5.)*0.4;
    return col;
}

vec3 textri2(in vec2 p, in float idx) {   
    float siz = 1920.0 * 0.02;  // 增加尺寸因子
    p *= 0.65;  // 增加密度
    vec2 q = abs(p);
    float rz = sin(clamp(max(q.x*1.73205+p.y, -p.y*2.)*15., 0., 25.))*siz+siz;
    vec3 col = (sin(vec3(1, 1.7, 5)*idx)+2.)*(rz+0.25);
    col -= sin(p.x*10.+time*5.)*0.2;
    return col;
}

vec3 texcub(in vec2 p, in float idx) {   
    float siz = 1920.0 * 0.02;  // 增加尺寸因子
    p *= 0.8;  // 增加密度
    float rz = sin(clamp(max(abs(p.x), abs(p.y))*12., 0., 25.))*siz+siz;
    vec3 col = (sin(vec3(4, 3., 5)*idx*0.9)+2.)*(rz+0.25);
    float a = atan(p.y, p.x);
    col -= sin(a*8.+time*11.)*0.15-0.15;
    return col;
}

vec3 textri(in vec2 p, in float idx) {	
    float siz = 1920.0 * 0.003;  // 增加尺寸因子
    p *= 0.65;  // 大幅增加密度
    vec2 bp = p;
    p.x *= 1.732;
    vec2 f = fract(p)-0.5;
    float d = abs(f.x-f.y);
    d = min(abs(f.x+f.y), d);
    
    float f1 = fract((p.y-0.25)*2.);
    d = min(d, abs(f1-0.5));
    d = 1.-smoothstep(0., 0.15/(siz+0.7), d);
    
    vec2 q = abs(bp);
    p = bp;
    d -= smoothstep(1., 1.3, (max(q.x*1.73205+p.y, -p.y*2.)));
    vec3 col = (sin(vec3(1., 1.5, 5)*idx)+2.)*((1.-d)+0.25);
    col -= sin(p.x*6.+time*8.)*0.15-0.1;
    return col;
}

//----------------------------------------------------------------------------
//----------------------------------球面平铺----------------------------
//----------------------------------------------------------------------------

// 十二面体：5个镜像五边形
vec3 dod(in vec3 p) {
    vec3 col = vec3(1);
    vec2 uv = vec2(0);
    for (float i = 0.; i <= 4.; i++) {
        p = roty(p, 0.81);
        p = rotx(p, 0.759);
        p = rotz(p, 0.3915);
        uv = vec2(p.z, p.y) / p.x;
        col = min(texpent(uv * 3.5, i+1.), col);  // 增加UV缩放
    }
    p = roty(p, 0.577);
    p = rotx(p, -0.266);
    p = rotz(p, -0.848);
    uv = vec2(p.z, -p.y) / p.x;
    col = min(texpent(uv * 3.5, 6.), col);  // 增加UV缩放
    
    return 1. - col;
}

// 二十面体：10个镜像三角形
vec3 ico(in vec3 p) {
    vec3 col = vec3(1);
    vec2 uv = vec2(0);
    
    // 中心带
    const float n1 = 0.7297;
    const float n2 = 1.0472;
    for (float i = 0.; i < 5.; i++) {
        if(mod(i, 2.) == 0.) {
            p = rotz(p, n1);
            p = rotx(p, n2);
        } else {
            p = rotz(p, n1);
            p = rotx(p, -n2);
        }
        uv = vec2(p.z, p.y) / p.x;
        col = min(textri(uv * 2.0, i+1.), col);  // 增加UV缩放
    }
    p = roty(p, 1.048);
    p = rotz(p, 0.8416);
    p = rotx(p, 0.7772);
    // 顶部帽
    for (float i = 0.; i < 5.; i++) {
        p = rotz(p, n1);
        p = rotx(p, n2);
        uv = vec2(p.z, p.y) / p.x;
        col = min(textri(uv * 2.0, i+6.), col);  // 增加UV缩放
    }
    
    return 1. - col;
}

// 八面体：4个镜像三角形
vec3 octa(in vec3 p) {
    vec3 col = vec3(1);
    vec2 uv = vec2(0);
    const float n1 = 1.231;
    const float n2 = 1.047;
    for (float i = 0.; i < 4.; i++) {
        p = rotz(p, n1);
        p = rotx(p, n2);
        uv = vec2(p.z, p.y) / p.x;
        col = min(textri2(uv * 1.8, i+1.), col);  // 增加UV缩放
    }
    
    return 1. - col;
}

// 立方体
vec3 cub(in vec3 p) {
    vec3 col = vec3(1);
    vec2 uv = vec2(p.z, p.y) / p.x;
    col = min(texcub(uv * 2.5, 15.), col);  // 增加UV缩放
    p = rotz(p, 1.5708);
    uv = vec2(p.z, p.y) / p.x;
    col = min(texcub(uv * 2.5, 4.), col);  // 增加UV缩放
    p = roty(p, 1.5708);
    uv = vec2(p.z, p.y) / p.x;
    col = min(texcub(uv * 2.5, 5.), col);  // 增加UV缩放
    
    return 1. - col;
}

void main() {
    // 使用从顶点着色器传来的本地归一化球面位置
    // 这里的 v_position 已经是相对于球体中心的位置，因此位置无关
    vec3 rd = normalize(v_position);
    
    // 添加旋转动画
    mat2 mx = mm2(time * 0.25);
    mat2 my = mm2(time * 0.27);
    rd.xz = mx * rd.xz;
    rd.xy = my * rd.xy;
    
    // 选择多面体类型（循环切换）
    float sel = mod(floor((time + 10.) * 0.2), 4.);
    
    vec3 col = vec3(0.);
    
    // 根据选择渲染不同的多面体
    if (sel < 0.5) {
        col = dod(rd) * 1.2;
    } else if (sel < 1.5) {
        col = ico(rd) * 1.2;
    } else if (sel < 2.5) {
        col = cub(rd) * 1.2;
    } else {
        col = octa(rd) * 1.2;
    }
    
    // 应用亮度
    col *= brightness;
    
    frag_color = vec4(col, v_color.a);
}
