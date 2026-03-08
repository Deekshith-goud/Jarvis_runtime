import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { AdditiveBlending, Points as ThreePoints, ShaderMaterial } from 'three';
import { useEventStore } from '../../store/eventStore';
import { coreVertexShader, coreFragmentShader } from './shaders/particleShaders';

const Particles = ({ count = 60000 }) => {
    const meshRef = useRef<ThreePoints>(null);
    const materialRef = useRef<ShaderMaterial>(null);
    const isListening = useEventStore(state => state.isListening);
    const agents = useEventStore(state => state.agents);

    // Calculate overall 'turbulence' based on agent activity
    const activeAgents = useMemo(() => {
        return Object.values(agents).filter(a => a.status === 'running' || a.status === 'thinking').length;
    }, [agents]);

    // Use a spring-like delay for turbulence so it doesn't snap instantly
    const turbulenceRef = useRef(0);
    const audioLevelRef = useRef(0);

    // Initial Fibonacci Sphere Geometry Setup
    const { basePositions, randomSeeds } = useMemo(() => {
        const p = new Float32Array(count * 3);
        const s = new Float32Array(count);
        const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle

        for (let i = 0; i < count; i++) {
            const y = 1 - (i / (count - 1)) * 2;
            const radius = Math.sqrt(1 - y * y);
            const theta = phi * i;

            // Expand the base position significantly
            const spread = 10.0;
            p[i * 3 + 0] = Math.cos(theta) * radius * spread; // x
            p[i * 3 + 1] = y * spread; // y
            p[i * 3 + 2] = Math.sin(theta) * radius * spread; // z

            s[i] = Math.random() * 100;
        }

        return { basePositions: p, randomSeeds: s };
    }, [count]);

    const uniforms = useMemo(() => ({
        uTime: { value: 0 },
        uAudioLevel: { value: 0 },
        uTurbulence: { value: 0 }
    }), []);

    useFrame((state, delta) => {
        if (!materialRef.current || !meshRef.current) return;

        // Animate Uniforms smoothly
        // Audio reactive
        const targetAudio = isListening ? 1.0 : 0.0;
        audioLevelRef.current += (targetAudio - audioLevelRef.current) * delta * 5.0;

        // Turbulence mapped strictly between 0.0 (calm) and 1.0 (chaotic)
        const targetTurbulence = Math.min(activeAgents * 0.5, 1.0);
        turbulenceRef.current += (targetTurbulence - turbulenceRef.current) * delta * 2.0;

        materialRef.current.uniforms.uTime.value = state.clock.getElapsedTime();
        materialRef.current.uniforms.uAudioLevel.value = audioLevelRef.current;
        materialRef.current.uniforms.uTurbulence.value = turbulenceRef.current;

        // Rotate the entire sphere slowly
        meshRef.current.rotation.y += delta * 0.1;
        meshRef.current.rotation.x += delta * 0.05;
    });

    return (
        <points ref={meshRef as any}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    args={[basePositions, 3]}
                />
                <bufferAttribute
                    attach="attributes-aBasePosition"
                    args={[basePositions, 3]}
                />
                <bufferAttribute
                    attach="attributes-aRandomSeed"
                    args={[randomSeeds, 1]}
                />
            </bufferGeometry>

            {/* Custom GLSL Material */}
            <shaderMaterial
                ref={materialRef}
                transparent
                depthWrite={false}
                blending={AdditiveBlending}
                vertexShader={coreVertexShader}
                fragmentShader={coreFragmentShader}
                uniforms={uniforms}
            />
        </points>
    );
};

export const CoreSphereCanvas: React.FC = () => {
    return (
        <div className="w-full h-full relative">
            <Canvas camera={{ position: [0, 0, 30], fov: 60 }} gl={{ alpha: true }}>
                <ambientLight intensity={0.5} />
                <Particles count={60000} />
            </Canvas>
        </div>
    );
};
