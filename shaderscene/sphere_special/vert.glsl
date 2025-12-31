#version 330
in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;
out vec4 v_color;
#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

uniform vec3 camera_position;
uniform float time;
uniform float brightness = 1.5;

// 常数定义
const float PI = 3.14159265359;
const float TAU = 6.28318530718;
const float PHI = 1.618033988749;
const float EPSILON = 1e-10;

// HG_SDF 函数
void pR(inout vec2 p, float a) {
    p = cos(a)*p + sin(a)*vec2(p.y, -p.x);
}

float pReflect(inout vec3 p, vec3 planeNormal, float offset) {
    float t = dot(p, planeNormal) + offset;
    if (t < 0.0) {
        p = p - (2.0 * t) * planeNormal;
    }
    return sign(t);
}

float smax(float a, float b, float r) {
    float m = max(a, b);
    if ((-a < r) && (-b < r)) {
        return max(m, -(r - sqrt((r+a)*(r+a) + (r+b)*(r+b))));
    } else {
        return m;
    }
}

// 20面体域镜像
vec3 nc;
vec3 pab;
vec3 pbc;
vec3 pca;
vec3 facePlane;
vec3 uPlane;
vec3 vPlane;

void initIcosahedron() {
    int Type = 5;
    float cospin = cos(PI/float(Type));
    float scospin = sqrt(0.75 - cospin*cospin);
    nc = vec3(-0.5, -cospin, scospin);
    pbc = vec3(scospin, 0.0, 0.5);
    pca = vec3(0.0, scospin, cospin);
    pbc = normalize(pbc);
    pca = normalize(pca);
    pab = vec3(0, 0, 1);
    
    facePlane = pca;
    uPlane = cross(vec3(1,0,0), facePlane);
    vPlane = vec3(1,0,0);
}

void pModIcosahedron(inout vec3 p) {
    p = abs(p);
    pReflect(p, nc, 0.0);
    p.xy = abs(p.xy);
    pReflect(p, nc, 0.0);
    p.xy = abs(p.xy);
    pReflect(p, nc, 0.0);
}

// 三角形平铺
const float sqrt3 = 1.7320508075688772;
const float i3 = 0.5773502691896258;
const mat2 cart2hex = mat2(1, 0, i3, 2.0 * i3);
const mat2 hex2cart = mat2(1, 0, -0.5, 0.5 * sqrt3);

struct TriPoints {
    vec2 a;
    vec2 b;
    vec2 c;
    vec2 center;
    vec2 ab;
    vec2 bc;
    vec2 ca;
};

TriPoints closestTriPoints(vec2 p) {    
    vec2 pTri = cart2hex * p;
    vec2 pi = floor(pTri);
    vec2 pf = fract(pTri);
    
    float split1 = step(pf.y, pf.x);
    float split2 = step(pf.x, pf.y);
    
    vec2 a = vec2(split1, 1);
    vec2 b = vec2(1, split2);
    vec2 c = vec2(0, 0);

    a += pi;
    b += pi;
    c += pi;

    a = hex2cart * a;
    b = hex2cart * b;
    c = hex2cart * c;
    
    vec2 center = (a + b + c) / 3.0;
    
    vec2 ab = (a + b) / 2.0;
    vec2 bc = (b + c) / 2.0;
    vec2 ca = (c + a) / 2.0;

    return TriPoints(a, b, c, center, ab, bc, ca);
}

// 测地线平铺
struct TriPoints3D {
    vec3 a;
    vec3 b;
    vec3 c;
    vec3 center;
    vec3 ab;
    vec3 bc;
    vec3 ca;
};

vec3 intersection(vec3 n, vec3 planeNormal, float planeOffset) {
    float denominator = dot(planeNormal, n);
    float t = (dot(vec3(0), planeNormal) + planeOffset) / -denominator;
    return n * t;
}

float faceRadius = 0.3819660112501051;

vec2 icosahedronFaceCoordinates(vec3 p) {
    vec3 pn = normalize(p);
    vec3 i = intersection(pn, facePlane, -1.0);
    return vec2(dot(i, uPlane), dot(i, vPlane));
}

vec3 faceToSphere(vec2 facePoint) {
    return normalize(facePlane + (uPlane * facePoint.x) + (vPlane * facePoint.y));
}

TriPoints3D geodesicTriPoints(vec3 p, float subdivisions) {
    vec2 uv = icosahedronFaceCoordinates(p);
    float uvScale = subdivisions / faceRadius / 2.0;
    TriPoints points = closestTriPoints(uv * uvScale);
    
    vec3 a = faceToSphere(points.a / uvScale);
    vec3 b = faceToSphere(points.b / uvScale);
    vec3 c = faceToSphere(points.c / uvScale);
    vec3 center = faceToSphere(points.center / uvScale);
    vec3 ab = faceToSphere(points.ab / uvScale);
    vec3 bc = faceToSphere(points.bc / uvScale);
    vec3 ca = faceToSphere(points.ca / uvScale);
    
    return TriPoints3D(a, b, c, center, ab, bc, ca);
}

// 光谱颜色调色板
vec3 pal(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b*cos(6.28318*(c*t+d));
}

vec3 spectrum(float n) {
    return pal(n, vec3(0.5,0.5,0.5), vec3(0.5,0.5,0.5), vec3(1.0,1.0,1.0), vec3(0.0,0.33,0.67));
}

// 动画参数
struct HexSpec {
    float roundTop;
    float roundCorner;
    float height;
    float thickness;
    float gap;    
};

HexSpec newHexSpec(float subdivisions) {
    return HexSpec(
        0.05 / subdivisions,
        0.1 / subdivisions,
        2.0,
        2.0,
        0.005
    );
}

// 动画函数
float animSubdivisions() {
    return mix(2.4, 3.4, cos(time * PI) * 0.5 + 0.5);
}

HexSpec animHex(vec3 hexCenter, float subdivisions) {
    HexSpec spec = newHexSpec(subdivisions);
    
    float offset = time * 3.0 * PI;
    offset -= subdivisions;
    float blend = dot(hexCenter, pca);
    blend = cos(blend * 30.0 + offset) * 0.5 + 0.5;
    spec.height = mix(1.75, 2.0, blend);
    spec.thickness = spec.height;

    return spec;
}

// 六边形模型
vec3 hexModel(vec3 p, vec3 hexCenter, vec3 edgeA, vec3 edgeB, HexSpec spec) {
    float edgeADist = dot(p, edgeA) + spec.gap;
    float edgeBDist = dot(p, edgeB) - spec.gap;
    float edgeDist = smax(edgeADist, -edgeBDist, spec.roundCorner);

    float outerDist = length(p) - spec.height;
    float d = smax(edgeDist, outerDist, spec.roundTop);

    float innerDist = length(p) - spec.height + spec.thickness;
    d = smax(d, -innerDist, spec.roundTop);
    
    // 颜色计算
    const vec3 FACE_COLOR = vec3(0.9, 0.9, 1.0);
    const vec3 BACK_COLOR = vec3(0.1, 0.1, 0.15);
    
    float faceBlend = (spec.height - length(p)) / spec.thickness;
    faceBlend = clamp(faceBlend, 0.0, 1.0);
    vec3 color = mix(FACE_COLOR, BACK_COLOR, step(0.5, faceBlend));
    
    vec3 edgeColor = spectrum(dot(hexCenter, pca) * 5.0 + length(p) + 0.8);    
    float edgeBlend = smoothstep(-0.04, -0.005, edgeDist);
    color = mix(color, edgeColor, edgeBlend);
    
    return color;
}

// 测地线模型
vec3 geodesicModel(vec3 p) {
    initIcosahedron();
    pModIcosahedron(p);
    
    float subdivisions = animSubdivisions();
    TriPoints3D points = geodesicTriPoints(p, subdivisions);
        
    vec3 edgeAB = normalize(cross(points.center, points.ab));
    vec3 edgeBC = normalize(cross(points.center, points.bc));
    vec3 edgeCA = normalize(cross(points.center, points.ca));
    
    // 计算三个六边形的颜色并混合
    HexSpec spec = animHex(points.b, subdivisions);
    vec3 colorB = hexModel(p, points.b, edgeAB, edgeBC, spec);
    
    spec = animHex(points.c, subdivisions);
    vec3 colorC = hexModel(p, points.c, edgeBC, edgeCA, spec);
    
    spec = animHex(points.a, subdivisions);
    vec3 colorA = hexModel(p, points.a, edgeCA, edgeAB, spec);
    
    // 简单的颜色混合
    return (colorA + colorB + colorC) / 3.0;
}

// 最终颜色计算
vec4 finalize_color(vec4 base_color, vec3 world_pos, vec3 unit_normal) {
    vec3 n = normalize(unit_normal);
    vec3 to_camera = normalize(camera_position - world_pos);
    
    // 模型旋转
    vec3 p = world_pos;
    pR(p.xz, time * PI/16.0);
    
    // 获取测地线颜色
    vec3 geodesic_color = geodesicModel(p);
    
    // Fresnel效果
    float fresnel = 1.0 - abs(dot(n, to_camera));
    fresnel = pow(fresnel, 1.2);
    
    // 基础光照
    vec3 lightPos = normalize(vec3(0.5, 0.5, -1.0));
    float amb = clamp((dot(n, vec3(0,1,0)) + 1.0) / 2.0, 0.0, 1.0);
    float dif = clamp(dot(n, lightPos), 0.0, 1.0);
    float bac = pow(clamp(dot(n, normalize(vec3(-0.5, -0.3, 1))), 0.0, 1.0), 1.5);
    float fre = pow(clamp(1.0 + dot(n, to_camera), 0.0, 1.0), 2.0);
    
    vec3 lin = vec3(0.0);
    lin += 1.2 * dif * vec3(0.9);
    lin += 0.8 * amb * vec3(0.5, 0.7, 0.8);
    lin += 0.3 * bac * vec3(0.25);
    lin += 0.2 * fre * vec3(1.0);
    
    // 最终颜色
    vec3 final_color = geodesic_color * lin;
    
    // 边缘发光
    final_color += vec3(0.3, 0.6, 1.0) * fresnel * 0.3;
    
    // 亮度调节
    final_color *= brightness;
    
    // Gamma校正
    final_color = pow(final_color, vec3(1.0 / 2.2));
    
    float alpha = 0.9 + 0.1 * fresnel;
    
    return vec4(final_color, alpha);
}

void main() {
    // 设置顶点位置
    emit_gl_Position(point);
    
    // 计算导数向量
    vec3 du = du_point - point;
    vec3 dv = dv_point - point;
    
    // 计算法向量
    vec3 normal = cross(du, dv);
    float normal_mag = length(normal);
    
    // 单位法向量
    vec3 unit_normal = (normal_mag < EPSILON) ?
        normalize(point) : normalize(normal);
    
    // 计算最终颜色
    v_color = finalize_color(rgba, point, unit_normal);
}
