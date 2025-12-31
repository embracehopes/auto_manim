#version 330
in vec3 v_position;
in vec2 v_uv;
in vec4 v_color;
out vec4 fragColor;

// Uniforms
uniform float time;
uniform float brightness;

#define STAR_LAYERS 4

// 程序化哈希（基于 vec2）
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

// 从整数网格生成四个随机值（模拟纹理采样）
vec4 getStarData2D(ivec2 cell, float layer) {
    // 合并 cell 和 layer 生成不同序列
    vec2 base = vec2(cell) + vec2(layer * 37.0, layer * 17.0);
    float a = hash(base + 0.123);
    float b = hash(base + 7.321);
    float c = hash(base + 42.0);
    float d = hash(base + 99.99);
    return vec4(a, b, c, d);
}

// 将平面星空算法映射到球面：使用顶点传来的 v_uv (0..1)
vec3 starsColoredFromUV(vec2 uv, float time_offset) {
    // 将 uv 从 [0,1] -> [-0.5, 0.5]
    vec2 p = uv - 0.5;
    // 修正宽高比（球面展开时可适当缩放 x）
    p.x *= 2.0;

    // 添加时间移动
    p.x += time_offset * 0.05;

    // 基于原始 Shadertoy 实现的多层星空
    vec2 uvm = (2.0 + p) * 128.0; // 初始单元格大小
    float sm = 1.0;
    float ex = -20.0;
    vec3 result = vec3(0.0);

    for (int i = 0; i < STAR_LAYERS; i++) {
        ivec2 cell = ivec2(floor(uvm));
        vec4 samp = getStarData2D(cell, float(i));

        vec2 offs = samp.rg - 0.5;
        vec2 cp = fract(uvm) - 0.5;
        float star = length(cp - offs * 0.9);
        float br = samp.b; // 基础亮度

        // 添加闪烁效果
        // 使用 cell 坐标和层数生成独特的闪烁模式
        float twinkle_seed = hash(vec2(cell) + vec2(float(i) * 13.7, float(i) * 7.3));
        float twinkle_speed = 2.0 + twinkle_seed * 3.0; // 闪烁速度 2.0-5.0
        float twinkle_phase = twinkle_seed * 6.28; // 随机相位
        float twinkle = 0.1 + 0.9 * sin(time * twinkle_speed + twinkle_phase); // 闪烁幅度 0.7-1.0

        // 应用闪烁到亮度
        br *= twinkle;

        float chroma = 0.5 + (samp.a - 0.5) * sm * 0.1;
        vec3 color = vec3(1.0 - chroma + pow(chroma, 5.0), 0.5, chroma);

        result += color * exp(ex * star) * sm * (br + 0.1);

        uvm *= 0.25; // 下层更稀疏
        sm *= 2.0;
        ex *= 2.0;
    }

    return result;
}

void main() {
    // 使用顶点着色器传来的 UV
    vec2 uv = v_uv;

    // 生成彩色星空
    vec3 col = starsColoredFromUV(uv, time);

    // 亮度控制
    col *= brightness;

    // 基础环境光，避免完全黑
    col += 0.02;

    col = clamp(col, 0.0, 1.0);
    fragColor = vec4(col, 1.0);
}
