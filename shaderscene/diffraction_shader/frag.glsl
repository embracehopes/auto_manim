/*
 * 光波干涉效应 Fragment Shader
 * 
 * 该着色器实现了多点光源的波干涉可视化效果。
 * 
 * 主要功能：
 * 1. 计算多个点光源在每个像素位置产生的复合波
 * 2. 支持球面波和平面波两种传播模式
 * 3. 实现基于距离的波衰减效果
 * 4. 提供振幅显示和强度显示两种可视化模式
 * 
 * 物理原理：
 * - 惠更斯原理：每个点光源产生球面波
 * - 波的叠加：复数振幅的矢量相加
 * - 衰减模型：(1+距离)^(-衰减因子)
 * 
 * 渲染技术：
 * - 使用复数表示波的振幅和相位
 * - 动态时间参数实现波的传播动画
 * - Alpha 通道基于波幅大小的平滑过渡
 */

#version 330

// 基础渲染参数
uniform vec3 color;           // 基础颜色
uniform float opacity;        // 整体透明度
uniform float frequency;      // 波的频率 (Hz)
uniform float wave_number;    // 波数 k = 2π/λ
uniform float max_amp;        // 最大振幅，用于归一化
uniform float n_sources;      // 活动光源数量
uniform float time;           // 当前时间，控制波的传播
uniform float decay_factor;   // 衰减指数

// 显示模式控制
uniform float show_intensity; // 0: 显示振幅, 1: 显示强度

/*
 * 点光源位置数组
 * 
 * 由于 ModernGL 对数组 uniform 的支持有限，
 * 这里使用单独的 vec3 uniform 变量来存储每个光源的位置。
 * 最多支持 32 个点光源的同时渲染。
 * 
 * 注意：在实际使用中，只有前 n_sources 个光源会参与计算
 */

// ModernGL 在处理数组类型的 uniform 时存在问题，
// 因此这里使用单独的 vec3 uniform 变量而非数组
uniform vec3 point_source0;
uniform vec3 point_source1;
uniform vec3 point_source2;
uniform vec3 point_source3;
uniform vec3 point_source4;
uniform vec3 point_source5;
uniform vec3 point_source6;
uniform vec3 point_source7;
uniform vec3 point_source8;
uniform vec3 point_source9;
uniform vec3 point_source10;
uniform vec3 point_source11;
uniform vec3 point_source12;
uniform vec3 point_source13;
uniform vec3 point_source14;
uniform vec3 point_source15;
uniform vec3 point_source16;
uniform vec3 point_source17;
uniform vec3 point_source18;
uniform vec3 point_source19;
uniform vec3 point_source20;
uniform vec3 point_source21;
uniform vec3 point_source22;
uniform vec3 point_source23;
uniform vec3 point_source24;
uniform vec3 point_source25;
uniform vec3 point_source26;
uniform vec3 point_source27;
uniform vec3 point_source28;
uniform vec3 point_source29;
uniform vec3 point_source30;
uniform vec3 point_source31;

// 输入输出变量
in vec3 frag_point;    // 从顶点着色器传入的片段世界坐标
out vec4 frag_color;   // 输出的片段颜色 (RGBA)

// 数学常量
const float TAU = 6.283185307179586;        // 2π，完整圆周
const float PLANE_WAVE_THRESHOLD = 999.0;   // 平面波阈值距离

/**
 * 计算单个光源在当前片段位置产生的复数振幅
 * 
 * @param source 光源位置 (如果距离 > PLANE_WAVE_THRESHOLD 则视为平面波)
 * @return vec2 复数振幅 (实部, 虚部)
 * 
 * 物理模型：
 * - 球面波：amplitude = A * exp(i*k*r) / (1+r)^decay_factor
 * - 平面波：amplitude = A * exp(i*k*z) / (1+r)^decay_factor
 * 其中 A 是源强度，k 是波数，r 是距离
 */
vec2 amp_from_source(vec3 source){
    float source_dist = length(source);
    // 判断是球面波还是平面波
    bool plane_wave = source_dist >= PLANE_WAVE_THRESHOLD;
    
    // 计算传播距离
    float dist = plane_wave ?
        source_dist - dot(frag_point, source / source_dist) :  // 平面波：投影距离
        distance(frag_point, source);                          // 球面波：实际距离

    // 计算波的相位：k*r - ω*t
    float term = TAU * (wave_number * dist - frequency * time);
    
    // 返回复数振幅：(cos(φ), sin(φ)) * 衰减因子
    return vec2(cos(term), sin(term)) * pow(1.0 + dist, -decay_factor);
}

void main() {
    // 透明度为 0 时直接丢弃片段，提高渲染性能
    if (opacity == 0) discard;

    // 设置基础颜色
    frag_color.rgb = color;
    
    // 将所有光源位置组织成数组以便遍历
    vec3 point_sources[32] = vec3[32](
        point_source0,
        point_source1,
        point_source2,
        point_source3,
        point_source4,
        point_source5,
        point_source6,
        point_source7,
        point_source8,
        point_source9,
        point_source10,
        point_source11,
        point_source12,
        point_source13,
        point_source14,
        point_source15,
        point_source16,
        point_source17,
        point_source18,
        point_source19,
        point_source20,
        point_source21,
        point_source22,
        point_source23,
        point_source24,
        point_source25,
        point_source26,
        point_source27,
        point_source28,
        point_source29,
        point_source30,
        point_source31
    );
    
    // 累加所有活动光源的复数振幅
    vec2 amp = vec2(0);
    for(int i = 0; i < int(n_sources); i++){
        amp += amp_from_source(point_sources[i]);
    }
    
    // 根据显示模式选择输出值
    // show_intensity=0: 显示振幅的实部（波的瞬时值）
    // show_intensity=1: 显示振幅的模长（波的强度）
    float magnitude = bool(show_intensity) ? length(amp) : amp.x;
    
    // 负值时反转颜色，用于可视化波的相位
    if (magnitude < 0) frag_color.rgb = 1.0 - frag_color.rgb;  

    // 基于波幅设置透明度，使用平滑过渡避免硬边缘
    frag_color.a = opacity * smoothstep(0, max_amp, abs(magnitude));
}