#version 120

uniform float u_eye_height;
uniform mat4 u_world_view;

attribute vec2 a_position;

varying vec3 v_position;
varying vec3 v_from_eye;

vec4 from_clipspace(vec2 position) {
    return vec4(position,-1.0,1.0);
}

vec3 from_water_to_eye(vec3 position) {
    vec4 eye_view=vec4(0.0,0.0,u_eye_height,1.0);
    vec4 eye=eye_view*u_world_view;
    return position-eye.xyz;
}

void main() {
    v_position=(from_clipspace(a_position)*u_world_view).xyz;
    v_from_eye=from_water_to_eye(v_position);
    gl_Position=vec4(a_position,0.0,1.0);
}
