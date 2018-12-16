#version 120

varying vec3 v_suncoord;
varying vec3 v_position;
varying float v_intensity;

void main() {
    float area_dst=length(cross(dFdx(v_position),dFdy(v_position)));
    float area_src=length(cross(dFdx(v_suncoord),dFdy(v_suncoord)));
    float concentration=area_src/area_dst;
    float intensity=v_intensity*concentration/8.0;
    gl_FragColor=vec4(intensity,intensity,intensity,1.0);
}
