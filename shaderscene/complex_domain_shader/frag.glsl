/*
 * 复变函数 Domain Coloring Fragment Shader
 * 
 * 实现复变函数的域着色可视化
 * 
 * 原理：
 * - 输入：复平面坐标 z = x + iy
 * - 计算：w = f(z) 的函数值
 * - 输出颜色：
 *   - Hue（色相）：由 arg(w)（辐角）决定
 *   - Lightness（明度）：由 |w|（模）决定
 *   - Saturation（饱和度）：固定或可调
 * 
 * 支持的函数类型（通过 func_type uniform 选择）：
 * 0: f(z) = z
 * 1: f(z) = z^2
 * 2: f(z) = z^3
 * 3: f(z) = 1/z
 * 4: f(z) = e^z
 * 5: f(z) = sin(z)
 * 6: f(z) = cos(z)
 * 7: f(z) = z^n (幂次由 power uniform 控制)
 * 8: f(z) = (z^2 - 1)/(z^2 + 1)
 * 9: f(z) = sin(1/z)
 * 10: f(z) = exp(1/z)
 * 11: f(z) = z * sin(1/z)
 * 12: f(z) = (z - a)(z - b)(z - c) 多项式（根由 root_a, root_b, root_c 控制）
 */

#version 330

// Uniform 参数
uniform float opacity;           // 透明度
uniform float func_type;         // 函数类型
uniform float power;             // 幂次（用于 z^n）
uniform float brightness_scale;  // 亮度缩放
uniform float saturation_scale;  // 饱和度缩放
uniform float time;              // 时间（用于动画）
uniform vec2 root_a;             // 多项式根 a
uniform vec2 root_b;             // 多项式根 b
uniform vec2 root_c;             // 多项式根 c

// 输入输出
in vec3 xyz_coords;
out vec4 frag_color;

// 引入通用函数
#INSERT finalize_color.glsl

// ========== 复数运算函数 ==========

// 复数乘法: (a + bi) * (c + di) = (ac - bd) + (ad + bc)i
vec2 cmul(vec2 a, vec2 b) {
    return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

// 复数除法
vec2 cdiv(vec2 a, vec2 b) {
    float denom = b.x * b.x + b.y * b.y + 1e-10;
    return vec2(
        (a.x * b.x + a.y * b.y) / denom,
        (a.y * b.x - a.x * b.y) / denom
    );
}

// 复数指数: e^(a + bi) = e^a * (cos(b) + i*sin(b))
vec2 cexp(vec2 z) {
    float ea = exp(z.x);
    return vec2(ea * cos(z.y), ea * sin(z.y));
}

// 复数对数: ln(z) = ln|z| + i*arg(z)
vec2 clog(vec2 z) {
    return vec2(0.5 * log(z.x * z.x + z.y * z.y + 1e-10), atan(z.y, z.x));
}

// 复数幂: z^n = e^(n * ln(z))
vec2 cpow(vec2 z, float n) {
    float r = length(z);
    if (r < 1e-10) return vec2(0.0);
    float theta = atan(z.y, z.x);
    float rn = pow(r, n);
    return vec2(rn * cos(n * theta), rn * sin(n * theta));
}

// 复数幂（复数指数）: z^w = e^(w * ln(z))
vec2 cpow_complex(vec2 z, vec2 w) {
    vec2 logz = clog(z);
    vec2 wlogz = cmul(w, logz);
    return cexp(wlogz);
}

// 复数正弦: sin(z) = (e^(iz) - e^(-iz)) / (2i)
vec2 csin(vec2 z) {
    vec2 iz = vec2(-z.y, z.x);
    vec2 niz = vec2(z.y, -z.x);
    vec2 eiz = cexp(iz);
    vec2 eniz = cexp(niz);
    vec2 diff = vec2(eiz.x - eniz.x, eiz.y - eniz.y);
    return vec2(diff.y / 2.0, -diff.x / 2.0);
}

// 复数余弦: cos(z) = (e^(iz) + e^(-iz)) / 2
vec2 ccos(vec2 z) {
    vec2 iz = vec2(-z.y, z.x);
    vec2 niz = vec2(z.y, -z.x);
    vec2 eiz = cexp(iz);
    vec2 eniz = cexp(niz);
    return vec2((eiz.x + eniz.x) / 2.0, (eiz.y + eniz.y) / 2.0);
}

// ========== HSL 转 RGB ==========

vec3 hsl2rgb(float h, float s, float l) {
    h = mod(h, 1.0);
    float c = (1.0 - abs(2.0 * l - 1.0)) * s;
    float x = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));
    float m = l - c / 2.0;
    
    vec3 rgb;
    if (h < 1.0/6.0) rgb = vec3(c, x, 0.0);
    else if (h < 2.0/6.0) rgb = vec3(x, c, 0.0);
    else if (h < 3.0/6.0) rgb = vec3(0.0, c, x);
    else if (h < 4.0/6.0) rgb = vec3(0.0, x, c);
    else if (h < 5.0/6.0) rgb = vec3(x, 0.0, c);
    else rgb = vec3(c, 0.0, x);
    
    return rgb + m;
}

// ========== 复数到颜色映射 ==========

vec3 complex_to_color(vec2 w) {
    // 检查无穷/NaN
    if (!isnan(w.x) && !isnan(w.y) && !isinf(w.x) && !isinf(w.y)) {
        float arg_w = atan(w.y, w.x);
        float mod_w = length(w);
        
        // Hue: 辐角映射到 [0, 1]
        float hue = (arg_w + 3.14159265) / (2.0 * 3.14159265);
        
        // Saturation
        float saturation = saturation_scale;
        
        // Lightness: 模的对数映射，避免极端值
        float lightness = 1.0 - 1.0 / (1.0 + log(1.0 + mod_w * brightness_scale));
        lightness = clamp(lightness, 0.2, 0.95);
        
        return hsl2rgb(hue, saturation, lightness);
    } else {
        return vec3(0.0);  // 黑色表示无穷/NaN
    }
}

// ========== 复变函数计算 ==========

vec2 compute_function(vec2 z) {
    int ftype = int(func_type);
    
    if (ftype == 0) {
        // f(z) = z
        return z;
    }
    else if (ftype == 1) {
        // f(z) = z^2
        return cmul(z, z);
    }
    else if (ftype == 2) {
        // f(z) = z^3
        return cmul(cmul(z, z), z);
    }
    else if (ftype == 3) {
        // f(z) = 1/z
        return cdiv(vec2(1.0, 0.0), z);
    }
    else if (ftype == 4) {
        // f(z) = e^z
        return cexp(z);
    }
    else if (ftype == 5) {
        // f(z) = sin(z)
        return csin(z);
    }
    else if (ftype == 6) {
        // f(z) = cos(z)
        return ccos(z);
    }
    else if (ftype == 7) {
        // f(z) = z^n
        return cpow(z, power);
    }
    else if (ftype == 8) {
        // f(z) = (z^2 - 1)/(z^2 + 1)
        vec2 z2 = cmul(z, z);
        return cdiv(z2 - vec2(1.0, 0.0), z2 + vec2(1.0, 0.0));
    }
    else if (ftype == 9) {
        // f(z) = sin(1/z)
        return csin(cdiv(vec2(1.0, 0.0), z));
    }
    else if (ftype == 10) {
        // f(z) = exp(1/z)
        return cexp(cdiv(vec2(1.0, 0.0), z));
    }
    else if (ftype == 11) {
        // f(z) = z * sin(1/z)
        return cmul(z, csin(cdiv(vec2(1.0, 0.0), z)));
    }
    else if (ftype == 12) {
        // f(z) = (z - a)(z - b)(z - c) 多项式
        vec2 za = z - root_a;
        vec2 zb = z - root_b;
        vec2 zc = z - root_c;
        return cmul(cmul(za, zb), zc);
    }
    else if (ftype == 13) {
        // f(z) = z^(1 + 10i) * cos((z-1)/(z^13 + z + 1)) 
        vec2 exp_part = cpow_complex(z, vec2(1.0, 10.0));
        vec2 z13 = cpow(z, 13.0);
        vec2 denom = z13 + z + vec2(1.0, 0.0);
        vec2 frac = cdiv(z - vec2(1.0, 0.0), denom);
        vec2 cos_part = ccos(frac);
        return cmul(exp_part, cos_part);
    }
    else if (ftype == 14) {
        // f(z) = ln(sin(z)) + cos(z)
        vec2 sin_z = csin(z);
        vec2 log_sin = clog(sin_z);
        vec2 cos_z = ccos(z);
        return log_sin + cos_z;
    }
    else if (ftype == 15) {
        // f(z) = exp(z) * sin(z)
        return cmul(cexp(z), csin(z));
    }
    else if (ftype == 16) {
        // f(z) = z^8 + 15*z^4 - 16
        vec2 z4 = cpow(z, 4.0);
        vec2 z8 = cmul(z4, z4);
        return z8 + 15.0 * z4 - vec2(16.0, 0.0);
    }
    else if (ftype == 17) {
        // f(z) = (z + z^2/sin(z^4 - 1))^2
        vec2 z2 = cmul(z, z);
        vec2 z4 = cmul(z2, z2);
        vec2 sin_part = csin(z4 - vec2(1.0, 0.0));
        vec2 inner = z + cdiv(z2, sin_part);
        return cmul(inner, inner);
    }
    else if (ftype == 18) {
        // 动画函数: f(z) = z^n，n 随时间变化
        float animated_power = 1.0 + mod(time, 4.0);
        return cpow(z, animated_power);
    }
    
    return z;
}

void main() {
    // 获取复平面坐标
    vec2 z = xyz_coords.xy;
    
    // 计算函数值
    vec2 w = compute_function(z);
    
    // 映射到颜色
    vec3 color = complex_to_color(w);
    
    // 输出最终颜色
    frag_color = finalize_color(
        vec4(color, opacity),
        xyz_coords,
        vec3(0.0, 0.0, 1.0)
    );
}
