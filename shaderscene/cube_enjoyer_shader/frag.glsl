#version 330

in vec4 v_color;
in vec2 v_uv;
in vec3 xyz_coords;

out vec4 frag_color;

uniform float time;
uniform float brightness = 1.5;
uniform vec2 resolution = vec2(1920.0, 1080.0);
uniform int use_orthographic = 1;  // 使用正交投影

#define TIME            time
#define RESOLUTION      resolution

#define PI              3.141592654
#define TAU             (2.0*PI)

#define TOLERANCE       0.0001
#define MAX_RAY_LENGTH  24.0
#define MAX_RAY_MARCHES 70
#define NORM_OFF        0.001
#define ROT(a)          mat2(cos(a), sin(a), -sin(a), cos(a))

#define ZOOM        (1.045)

#define FWD(x)      exp2((x)*ZOOM)
#define REV(x)      (log2(x)/ZOOM)

// HSV to RGB conversion
const vec4 hsv2rgb_K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
vec3 hsv2rgb(vec3 c) {
  vec3 p = abs(fract(c.xxx + hsv2rgb_K.xyz) * 6.0 - hsv2rgb_K.www);
  return c.z * mix(hsv2rgb_K.xxx, clamp(p - hsv2rgb_K.xxx, 0.0, 1.0), c.y);
}

#define HSV2RGB(c)  (c.z * mix(hsv2rgb_K.xxx, clamp(abs(fract(c.xxx + hsv2rgb_K.xyz) * 6.0 - hsv2rgb_K.www) - hsv2rgb_K.xxx, 0.0, 1.0), c.y))

// Color constants
const float hoff      = 0.0;
const vec3 skyCol     = HSV2RGB(vec3(hoff+0.57, 0.70, 0.25));
const vec3 glowCol0   = HSV2RGB(vec3(hoff+0.05, 0.85, 0.00125));
const vec3 glowCol1   = HSV2RGB(vec3(hoff+0.55, 0.85, 0.05));
const vec3 sunCol1    = HSV2RGB(vec3(hoff+0.60, 0.50, 0.5));
const vec3 sunCol2    = HSV2RGB(vec3(hoff+0.05, 0.75, 25.0));
const vec3 diffCol    = HSV2RGB(vec3(hoff+0.45, 0.5, 0.25));
const vec3 sunDir1    = normalize(vec3(3.0, 3.0, -7.0));

// Rotation matrices
mat3 rotX(float a) {
  float c = cos(a);
  float s = sin(a);
  return mat3(
    1.0 , 0.0 , 0.0,
    0.0 , +c  , +s,
    0.0 , -s  , +c
  );
}

mat3 rotY(float a) {
  float c = cos(a);
  float s = sin(a);
  return mat3(
    +c  , 0.0 , +s,
    0.0 , 1.0 , 0.0,
    -s  , 0.0 , +c
  );
}

mat3 rotZ(float a) {
  float c = cos(a);
  float s = sin(a);
  return mat3(
    +c  , +s  , 0.0,
    -s  , +c  , 0.0,
    0.0 , 0.0 , 1.0
  );
}

// ACES tonemapping
vec3 aces_approx(vec3 v) {
  v = max(v, 0.0);
  v *= 0.6;
  float a = 2.51;
  float b = 0.03;
  float c = 2.43;
  float d = 0.59;
  float e = 0.14;
  return clamp((v*(a*v+b))/(v*(c*v+d)+e), 0.0, 1.0);
}

float rayPlane(vec3 ro, vec3 rd, vec4 p) {
  return -(dot(ro,p.xyz)+p.w)/dot(rd,p.xyz);
}

// Distance functions
float box(vec2 p, vec2 b) {
  vec2 d = abs(p)-b;
  return length(max(d,0.0)) + min(max(d.x,d.y),0.0);
}

float box(vec3 p, vec3 b) {
  vec3 q = abs(p) - b;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
}

float boxf(vec3 p, vec3 b, float e) {
       p = abs(p  )-b;
  vec3 q = abs(p+e)-e;
  return min(min(
      length(max(vec3(p.x,q.y,q.z),0.0))+min(max(p.x,max(q.y,q.z)),0.0),
      length(max(vec3(q.x,p.y,q.z),0.0))+min(max(q.x,max(p.y,q.z)),0.0)),
      length(max(vec3(q.x,q.y,p.z),0.0))+min(max(q.x,max(q.y,p.z)),0.0));
}

float sphere4(vec3 p, float r) {
  p *= p;
  return pow(dot(p, p), 0.25) - r;
}

mat3 g_rot;
float g_gd;

float df(vec3 p) {
  p *= g_rot;
  float d0 = box(p, vec3(3.0));
  float d1 = boxf(p, vec3(3.01), 0.0)-0.015;
  float d3 = sphere4(p, 3.0);
  
  vec3 p2 = p;
  p2 = abs(p2);
  p2 -= 3.0;
  
  float fp2 = FWD(length(p2));
  float n = floor(fp2);
  
  float x0 = REV(n);
  float x1 = REV(n+1.0);

  float m = (x0+x1)*0.5;
  float w = x1-x0;
  
  float d2 = abs(length(p2)-m)-(w*0.5)+0.025;

  d0 = max(d0, d2);
  d0 = max(d0, -(d1-0.03));

  float d = d0;
  d = min(d, d1);
  d = min(d, d3);
  
  float gd = d1;
  gd = min(gd, d3);
  g_gd = min(g_gd, gd);
  
  return d;
}

vec3 normal(vec3 pos) {
  vec2 eps = vec2(NORM_OFF,0.0);
  vec3 nor;
  nor.x = df(pos+eps.xyy) - df(pos-eps.xyy);
  nor.y = df(pos+eps.yxy) - df(pos-eps.yxy);
  nor.z = df(pos+eps.yyx) - df(pos-eps.yyx);
  return normalize(nor);
}

float rayMarch(vec3 ro, vec3 rd, out int iter) {
  float t = 0.0;
  vec2 dti = vec2(1e10,0.0);
  int i = 0;
  for (i = 0; i < MAX_RAY_MARCHES; ++i) {
    float d = df(ro + rd*t);
    if (d<dti.x) { dti=vec2(d,t); }
    if (d < TOLERANCE || t > MAX_RAY_LENGTH) {
      break;
    }
    t += d;
  }
  
  iter = i;
  return t;
}

vec3 render0(vec3 ro, vec3 rd) {
  vec3 col = vec3(0.0);
  float sd = max(dot(sunDir1, rd), 0.0);

  col += clamp(vec3(1.0/abs(rd.y))*glowCol0, 0.0, 1.0);
  col += 0.75*skyCol*pow((1.0-abs(rd.y)), 8.0);
  col += 2.0*sunCol1*pow(sd, 100.0);
  col += sunCol2*pow(sd, 800.0);

  float tp1 = rayPlane(ro, rd, vec4(vec3(0.0, -1.0, 0.0), -6.0));

  if (tp1 > 0.0) {
    vec3 pos = ro + tp1*rd;
    vec2 pp = pos.xz;
    float db = box(pp, vec2(5.0, 9.0))-3.0;
    
    col += vec3(4.0)*skyCol*rd.y*rd.y*smoothstep(0.25, 0.0, db);
    col += vec3(0.8)*skyCol*exp(-0.5*max(db, 0.0));
    col += 0.25*sqrt(skyCol)*max(-db, 0.0);
  }

  return clamp(col, 0.0, 10.0);
}

vec3 render1(vec3 ro, vec3 rd, vec2 sp) {
  g_gd = 1E3;
  int iter;
  float t = rayMarch(ro, rd, iter);
  vec3 ggcol = (glowCol1)*inversesqrt(max(g_gd, 0.00025));
  vec3 col = render0(ro, rd);

  vec3 p = ro+rd*t;
  vec3 n = normal(p);
  vec3 r = reflect(rd, n);
  float fre0 = 1.0+dot(rd, n);
  float fre = fre0;
  fre *= fre;
  float dif = dot(sunDir1, n); 

  float ao = 1.0-float(iter)/float(MAX_RAY_MARCHES);
  float fo = mix(0.2, 0.5, ao);
  if (t < MAX_RAY_LENGTH) {
    col = vec3(0.0);
    col += sunCol1*dif*dif*diffCol*fo;
    col += mix(0.33, 1.0, fre)*render0(p, r)*fo;
  }
  
  col += clamp(ggcol, 0.0, 4.0);
  return col;
}

vec3 effect(vec2 p, vec2 pp) {
  float tm = TIME*0.5+10.0;
  
  // 固定的正视角度，使用正交投影
  g_rot = rotX(0.333*tm)*rotZ(0.5*tm)*rotY(0.23*tm);
  
  vec3 ro, rd;
  
  if (use_orthographic == 1) {
    // 正交投影 - 所有光线平行
    ro = vec3(p.x * 4.0, p.y * 4.0, 10.0);  // 在平面上分布起点
    rd = vec3(0.0, 0.0, -1.0);  // 所有光线都朝-Z方向
  } else {
    // 透视投影（原来的方式）
    ro = vec3(0.0, 0.0, 10.0);
    const vec3 la = vec3(0.0, 0.0, 0.0);
    const vec3 up = normalize(vec3(0.0, 1.0, 0.0));

    vec3 ww = normalize(la - ro);
    vec3 uu = normalize(cross(up, ww));
    vec3 vv = (cross(ww,uu));
    const float fov = tan(TAU/6.0);
    rd = normalize(-p.x*uu + p.y*vv + fov*ww);
  }

  vec3 col = render1(ro, rd, p);
  col -= 0.05*length(pp);
  col *= smoothstep(1.5, 0.5, length(pp));

  col = aces_approx(col); 
  col = sqrt(col);
  
  return col;
}

void main() {
    // 使用UV坐标，范围从[0,1]转换到[-1,1]
    vec2 q = v_uv;
    vec2 p = -1.0 + 2.0 * q;
    vec2 pp = p;
    
    vec3 col = effect(p, pp);
    
    // 应用亮度
    col *= brightness;
    
    frag_color = vec4(col, 1.0);
}
