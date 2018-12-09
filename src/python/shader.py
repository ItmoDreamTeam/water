VERTEX_SHADER = ("""
#version 120

uniform float u_eye_height;
uniform mat4 u_world_view;
uniform float u_alpha;
uniform float u_bed_depth;

attribute vec2 a_position;
attribute float a_height;
attribute vec2 a_normal;

varying vec3 v_normal;
varying vec3 v_position;
varying vec3 v_reflected;
varying vec2 v_sky_texcoord;
varying vec2 v_bed_texcoord;
varying float v_reflectance;
varying vec3 v_mask;

void main (void) {
    v_position=vec3(a_position.xy,a_height);
    v_normal=normalize(vec3(a_normal, -1));

    vec4 position_view=u_world_view*vec4(v_position,1);
    float z=1-(1+position_view.z)/(1+u_eye_height);
    gl_Position=vec4(position_view.xy,-position_view.z*z,z);

    vec4 eye_view=vec4(0,0,u_eye_height,1);
    vec4 eye=transpose(u_world_view)*eye_view;
    vec3 from_eye=normalize(v_position-eye.xyz);
    vec3 normal=normalize(-v_normal);
    v_reflected=normalize(from_eye-2*normal*dot(normal,from_eye));
    v_sky_texcoord=0.05*v_reflected.xy/v_reflected.z+vec2(0.5,0.5);

    vec3 cr=cross(normal,from_eye);
    float d=1-u_alpha*u_alpha*dot(cr,cr);
    float c2=sqrt(d);
    vec3 refracted=normalize(u_alpha*cross(cr,normal)-normal*c2);
    float c1=-dot(normal,from_eye);

    float t=(-u_bed_depth-v_position.z)/refracted.z;
    vec3 point_on_bed=v_position+t*refracted;
    v_bed_texcoord=point_on_bed.xy+vec2(0.5,0.5);

    float reflectance_s=pow((u_alpha*c1-c2)/(u_alpha*c1+c2),2);
    float reflectance_p=pow((u_alpha*c2-c1)/(u_alpha*c2+c1),2);
    v_reflectance=(reflectance_s+reflectance_p)/2;

    float diw=length(point_on_bed-v_position);
    vec3 filter=vec3(1,0.5,0.2);
    v_mask=vec3(exp(-diw*filter.x),exp(-diw*filter.y),exp(-diw*filter.z));
}
""")

TRIANGLE_FRAGMENT_SHADER = ("""
#version 120
uniform sampler2D u_sky_texture;
uniform sampler2D u_bed_texture;
uniform vec3 u_sun_direction;
uniform vec3 u_sun_diffused_color;
uniform vec3 u_sun_reflected_color;

uniform float u_reflected_mult;
uniform float u_diffused_mult;
uniform float u_bed_mult;
uniform float u_depth_mult;
uniform float u_sky_mult;

varying vec3 v_normal;
varying vec3 v_position;
varying vec3 v_reflected;
varying vec2 v_sky_texcoord;
varying vec2 v_bed_texcoord;
varying float v_reflectance;
varying vec3 v_mask;

void main() {
    vec3 sky_color=texture2D(u_sky_texture, v_sky_texcoord).rgb;
    vec3 bed_color=texture2D(u_bed_texture, v_bed_texcoord).rgb;

    vec3 normal=normalize(v_normal);
    float diffused_intensity=u_diffused_mult*max(0, -dot(normal, u_sun_direction));
    float cosphi=max(0,dot(u_sun_direction,normalize(v_reflected)));
    float reflected_intensity=u_reflected_mult*pow(cosphi,100);

    vec3 ambient_water=vec3(0,0.3,0.5);
    vec3 image_color=u_bed_mult*bed_color*v_mask+u_depth_mult*ambient_water*(1-v_mask);

    vec3 rgb=u_sky_mult*sky_color*v_reflectance+image_color*(1-v_reflectance)
        +diffused_intensity*u_sun_diffused_color+reflected_intensity*u_sun_reflected_color;
    gl_FragColor.rgb = clamp(rgb,0.0,1.0);
    gl_FragColor.a = 1;
}
""")

POINT_FRAGMENT_SHADER = """
#version 120

void main() {
    gl_FragColor = vec4(1,0,0,1);
}
"""
