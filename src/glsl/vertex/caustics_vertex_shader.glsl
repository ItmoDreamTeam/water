#version 120

uniform float u_eye_height;
uniform mat4 u_world_view;
uniform vec3 u_sun_direction;
uniform float u_bed_depth;
uniform float u_alpha;

attribute vec2 a_position;
attribute float a_height;
attribute vec2 a_normal;

varying vec3 v_suncoord;
varying vec3 v_position;
varying float v_intensity;

float refraction(vec3 incident, vec3 outer_normal, float alpha, out vec3 refracted) {
    float c1=dot(outer_normal,incident);
    if(c1>0.0) return 0.0;
    float k=max(0.0, 1.0-alpha*alpha*(1.0-c1*c1));
    refracted=normalize(alpha*incident-(alpha*c1+sqrt(k))*outer_normal);
    float c2=dot(refracted,outer_normal);
    float reflectance_s=pow((alpha*c1-c2)/(alpha*c1+c2),2.0);
    float reflectance_p=pow((alpha*c2-c1)/(alpha*c2+c1),2.0);
    return (reflectance_s+reflectance_p)/2.0;
}

vec3 bed_intersection(vec3 position, vec3 direction) {
    float t=(-u_bed_depth-position.z)/direction.z;
    return position+t*direction;
}

vec4 to_clipspace(vec3 position) {
    vec4 position_view=u_world_view*vec4(position,1);
    float z=1.0-(1.0+position_view.z)/(1.0+u_eye_height);
    return vec4(position_view.xy,-position_view.z*z/2.0,z);
}

void main() {
    vec3 position=vec3(a_position,a_height);
    vec3 outer_normal=-normalize(vec3(a_normal,-1.0));
    // Compute projection to orthogonal to sun plane
    // to compute amount of light per fragment.
    v_suncoord=position-u_sun_direction*dot(u_sun_direction, position);
    // Compute refracted ray
    vec3 refracted;
    v_intensity=1.0-refraction(-u_sun_direction, outer_normal, u_alpha, refracted);
    // compute projection to bed
    vec3 on_bed=bed_intersection(position,refracted);
    vec4 point=to_clipspace(vec3(on_bed.xy, -1));
    gl_Position=point;
    v_position=vec3(on_bed.xy,1.0);
}
