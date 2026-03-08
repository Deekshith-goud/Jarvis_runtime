import React, { useRef, useEffect } from 'react';


export const VoiceWaveform: React.FC<{ active: boolean }> = ({ active }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId: number;
        let time = 0;

        const render = () => {
            time += 0.05;

            // Clear canvas with transparent fade for motion blur
            ctx.fillStyle = 'rgba(10, 15, 29, 0.3)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const centerY = canvas.height / 2;
            const amplitude = active ? 12 : 1.5; // Flat when inactive, bouncy when active
            const frequency = 0.02;

            // Draw two glowing sine waves
            for (let w = 0; w < 2; w++) {
                ctx.beginPath();
                for (let x = 0; x < canvas.width; x++) {
                    const y = centerY + Math.sin(x * frequency + time + w * Math.PI) * amplitude * Math.sin(x * 0.01);
                    if (x === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }

                ctx.strokeStyle = w === 0 ? 'rgba(0, 240, 255, 0.8)' : 'rgba(139, 92, 246, 0.5)';
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    }, [active]);

    return (
        <div className={`transition-opacity duration-500 w-32 h-8 ${active ? 'opacity-100' : 'opacity-40'}`}>
            <canvas
                ref={canvasRef}
                width={128}
                height={32}
                className="w-full h-full"
            />
        </div>
    );
};
