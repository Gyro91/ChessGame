/*  ___| |__   __ _  __| | _____      __  _ __ ___   __ _ _ __  v.02
 * / __| '_ \ / _` |/ _` |/ _ \ \ /\ / / | '_ ` _ \ / _` | '_ \/ __|
 * \__ \ | | | (_| | (_| | (_) \ V  V /  | | | | | | (_| | |_) \__ \
 * |___/_| |_|\__,_|\__,_|\___/ \_/\_/   |_| |_| |_|\__,_| .__/|___/
 * XVR tutorial example on shadow mapping                |_|jul 2006
 *
 * Need help with this code? Please contact:
 *  - d.vercelli@sssup.it
 * 
 * Need help with XVR? Please contact:
 *  - http://wiki.vrmedia.it
 *  - http://forums.vrmedia.it
 */

[VERTEX SHADER]

varying vec4 shadowTexCoord;

void pointLight()
{
	int i = 0; // light index
	
	// Compute vector from surface to light position
	vec3 VP = normalize(vec3(gl_LightSource[i].position - gl_ModelViewMatrix * gl_Vertex));

	float nDotVP, nDotHV;
	{
		// Compute the normal in eye coordinates
		vec3 normal = normalize(gl_NormalMatrix * gl_Normal);

		// normal . light direction
		nDotVP = max(0.0, dot(normal, VP));

		// direction of maximum highlights (eye)
		vec3 halfVector = normalize(VP + vec3(0.0, 0.0, 1.0));
		
		// normal . light half vector
		nDotHV = max(0.0, dot(normal, halfVector));
	}

	// power factor
	float pf = (nDotVP == 0.0) ? 0.0 : pow(nDotHV, gl_FrontMaterial.shininess);

	// Ambient
	vec4 color = gl_FrontMaterial.ambient * gl_LightSource[i].ambient;

	// Diffuse
	color += gl_FrontMaterial.diffuse * gl_LightSource[i].diffuse * nDotVP;

	// Specular
	color += gl_FrontMaterial.specular * gl_LightSource[i].specular * pf;

	float attenuation;
	{
		// Compute distance between surface and light position
		float d = length(VP);
	
		// Compute attenuation
		attenuation = 1.0 / (gl_LightSource[i].constantAttenuation +
			d * (gl_LightSource[i].linearAttenuation + d * gl_LightSource[i].quadraticAttenuation));
	}

	gl_FrontColor = clamp(color * attenuation + gl_FrontLightModelProduct.sceneColor, 0.0, 1.0);
}

void main (void)
{
	// vertex calculation
	gl_Position = ftransform();

	// color calculations
	pointLight();

	// shadow texture coordinates generation
	shadowTexCoord = gl_TextureMatrix[0] * gl_ModelViewMatrix * gl_Vertex;
	gl_TexCoord[0] = gl_MultiTexCoord0;
}

[FRAGMENT SHADER]

uniform sampler2DShadow shadowMap;
uniform sampler2D tex;

uniform bool is_textured;

varying vec4 shadowTexCoord;

void main(void)
{
//	float s = shadowTexCoord.z/shadowTexCoord.w - texture2DProj(shadowMap, shadowTexCoord).r;
	vec4 orig_color = gl_Color;
	
	//if (is_textured)
	orig_color *= texture2D(tex, gl_TexCoord[0].st);

	if (shadow2DProj(shadowMap, shadowTexCoord).r == 1.0)
		gl_FragColor = 1.0*orig_color;		//2*orig_color;
	else
		gl_FragColor = vec4(vec3(0.0), 1.0) * 1.0 + orig_color * 0.5;		//vec4(vec3(0.0), 1.0) * 1.5 + orig_color * 1.0;

}
