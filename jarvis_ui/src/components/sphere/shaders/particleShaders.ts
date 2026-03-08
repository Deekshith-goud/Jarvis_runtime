import { snoise3D } from './noise';

// Vertex Shader
export const coreVertexShader = `
${snoise3D}

uniform float uTime;
uniform float uAudioLevel;
uniform float uTurbulence;

attribute vec3 aBasePosition;
attribute float aRandomSeed;

varying vec3 vPosition;
varying float vNoise;

void main() {
    // 1. Calculate base radius including voice reactivity
    float radiusPhase = uTime * 2.0 + aRandomSeed;
    float audioRipple = sin(radiusPhase) * uAudioLevel * 0.2;
    float expandedRadius = 4.0 + audioRipple;
    
    // Scale base position by base radius
    vec3 pos = aBasePosition * expandedRadius;
    
    // 2. Simplex Noise Flow Field Displacements
    // Scale down the time for smooth drifting
    float timeSlow = uTime * 0.15;
    
    // Create turbulent motion if agents are active, otherwise calm breathing
    float noiseFreq = mix(0.5, 1.5, uTurbulence);
    float noiseAmp = mix(0.2, 1.5, uTurbulence);
    
    vec3 noisePos = pos * noiseFreq + timeSlow;
    
    // Calculate a curl-like vector using snoise
    float nx = snoise(noisePos + vec3(0.0, 0.0, 0.0));
    float ny = snoise(noisePos + vec3(12.3, 45.6, 78.9));
    float nz = snoise(noisePos + vec3(98.7, 65.4, 32.1));
    vec3 displacement = vec3(nx, ny, nz) * noiseAmp;
    
    // Add flow field displacement
    pos += displacement;
    
    // Pass noise intensity to fragment for color mapping
    vNoise = (nx + ny + nz) / 3.0; // range Roughly ~[-1, 1]
    vPosition = pos;
    
    // Calculate final position using standard modelMatrix not instanceMatrix
    vec4 mvPosition = viewMatrix * modelMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mvPosition;
    
    // Base particle size - much larger to be visible
    gl_PointSize = mix(4.0, 15.0, aRandomSeed / 100.0);
    // Attenuate point size based on depth
    gl_PointSize *= (30.0 / -mvPosition.z);
}
`;

// Fragment Shader
export const coreFragmentShader = `
uniform float uTurbulence;

varying vec3 vPosition;
varying float vNoise;

void main() {
    // Create a circular point instead of square
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    float r = dot(cxy, cxy);
    if (r > 1.0) {
        discard;
    }
    
    // Soft edge blending
    float alpha = 1.0 - r;
    alpha = pow(alpha, 1.5);
    
    // Colors: #00f0ff (cyan) and deeper electric blues
    vec3 cyan = vec3(0.0, 0.94, 1.0);
    vec3 deepBlue = vec3(0.0, 0.2, 0.8);
    vec3 hotWhite = vec3(0.8, 0.9, 1.0);
    
    // Map noise to color, shifting hot when turbulent
    float normalizedNoise = (vNoise + 1.0) * 0.5; // 0 to 1
    
    vec3 finalColor = mix(deepBlue, cyan, normalizedNoise);
    
    // If high turbulence, push the brightest points toward white
    finalColor = mix(finalColor, hotWhite, normalizedNoise * uTurbulence * 0.8);
    
    // Base opacity fades near 0
    float finalAlpha = alpha * 0.6;
    
    gl_FragColor = vec4(finalColor, finalAlpha);
}
`;
