#version 120

uniform sampler2D u_sky_texture;
uniform sampler2D u_bed_texture;
uniform vec3 u_sun_direction;
uniform vec3 u_sun_reflected_color;
uniform vec3 u_water_ambient_color;
uniform float u_bed_depth;
uniform float u_reflected_mult;
uniform float u_bed_mult;
uniform float u_depth_mult;
uniform float u_sky_mult;

varying vec3 v_position;
varying vec3 v_from_eye;

vec2 get_sky_texcoord(vec3 position, vec3 direction) {
    return 0.05*direction.xy/direction.z+vec2(0.5,0.5);
}

vec3 bed_intersection(vec3 position, vec3 direction) {
    float t=(-u_bed_depth-position.z)/direction.z;
    return position+t*direction;
}

vec2 get_bed_texcoord(vec3 point_on_bed) {
    return point_on_bed.xy+vec2(0.5,0.5);
}

vec3 sun_contribution(vec3 direction) {
    float cosphi=max(dot(u_sun_direction,direction), 0.0);
    float reflected_intensity=u_reflected_mult*pow(cosphi,100.0);
    return reflected_intensity*u_sun_reflected_color;
}

vec3 water_decay(vec3 color, float distance) {
    float mask=exp(-distance*u_depth_mult);
    return mix(u_water_ambient_color, color, mask);
}

void main() {
    // normalize directions
    vec3 from_eye=normalize(v_from_eye);
    // compute color
    vec3 rgb;
    if(from_eye.z>=0.0) { // looking at the sky
        vec2 sky_texcoord;
        sky_texcoord=get_sky_texcoord(v_position, from_eye);
        vec3 sky_color=texture2D(u_sky_texture, sky_texcoord).rgb;
        rgb=u_sky_mult*sky_color+sun_contribution(from_eye);
    } else { // looking at the seabed
        vec2 bed_texcoord;
        float path_in_water;
        vec3 point_on_bed=bed_intersection(v_position, from_eye);
        bed_texcoord=get_bed_texcoord(point_on_bed);
        if(dot(from_eye,point_on_bed-v_position)>0.0)
            path_in_water=length(point_on_bed-v_position);
        else path_in_water=0.0;
        vec3 bed_color=texture2D(u_bed_texture, bed_texcoord).rgb;
        rgb=water_decay(bed_color*u_bed_mult, path_in_water);
    };
    gl_FragColor.rgb = clamp(rgb,0.0,1.0);
    gl_FragColor.a = 1.0;
}
