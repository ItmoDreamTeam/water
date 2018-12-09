VERTEX_SHADER = ("""
#version 120

uniform float u_eye_height;

attribute vec2 a_position;
attribute float a_height;
attribute vec2 a_normal;

varying vec3 v_normal;
varying vec3 v_position;

void main (void) {
    v_normal=normalize(vec3(a_normal, -1));
    v_position=vec3(a_position.xy,a_height);

    // [-1,u_eye_height] -> [1,0] 
    float z=1-(1+a_height)/(1+u_eye_height);
    gl_Position=vec4(a_position.xy,a_height*z,z);
}
""")

TRIANGLE_FRAGMENT_SHADER = ("""
#version 120
uniform sampler2D u_sky_texture;
uniform sampler2D u_bed_texture;
uniform float u_alpha;
uniform float u_bed_depth;
uniform float u_eye_height;

varying vec3 v_normal;
varying vec3 v_position;

void main() {
    vec3 eye=vec3(0,0,u_eye_height);
    vec3 from_eye=normalize(v_position-eye);
    vec3 normal=normalize(-v_normal);
    vec3 reflected=normalize(from_eye-2*normal*dot(normal,from_eye));

    vec2 sky_texcoord=0.25*reflected.xy/reflected.z+vec2(0.5,0.5);
    vec3 sky_color=texture2D(u_sky_texture, sky_texcoord).rgb;

    vec3 cr=cross(normal,from_eye);
    float d=1-u_alpha*u_alpha*dot(cr,cr);
    float c2=sqrt(d);
    vec3 refracted=normalize(u_alpha*cross(cr,normal)-normal*c2);
    float c1=-dot(normal,from_eye);

    float t=(-u_bed_depth-v_position.z)/refracted.z;
    vec3 point_on_bed=v_position+t*refracted;
    vec2 bed_texcoord=point_on_bed.xy+vec2(0.5,0.5);
    vec3 bed_color=texture2D(u_bed_texture, bed_texcoord).rgb;

    float reflectance_s=pow((u_alpha*c1-c2)/(u_alpha*c1+c2),2);
    float reflectance_p=pow((u_alpha*c2-c1)/(u_alpha*c2+c1),2);
    float reflectance=(reflectance_s+reflectance_p)/2;

    float diw=length(point_on_bed-v_position);
    vec3 filter=vec3(1,0.5,0.2);
    vec3 mask=vec3(exp(-diw*filter.x),exp(-diw*filter.y),exp(-diw*filter.z));
    vec3 ambient_water=vec3(0,0.6,0.8);
    vec3 image_color=bed_color*mask+ambient_water*(1-mask);

    vec3 rgb=sky_color*reflectance+image_color*(1-reflectance);
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