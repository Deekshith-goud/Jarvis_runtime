import React from 'react';
import { useEventStore } from '../../store/eventStore';
import { Activity, GripHorizontal } from 'lucide-react';

const ProgressBar = ({ label, value, colorClass }: { label: string, value: number, colorClass: string }) => (
    <div className="flex flex-col gap-1 w-full">
        <div className="flex justify-between text-xs font-mono">
            <span className="text-gray-400">{label}</span>
            <span className={colorClass}>{value.toFixed(1)}%</span>
        </div>
        <div className="h-1.5 w-full bg-navy-900 rounded-full overflow-hidden border border-cyan-vivid/10">
            <div
                className={`h-full transition-all duration-500 ease-out ${colorClass.replace('text-', 'bg-')} shadow-[0_0_10px_currentColor]`}
                style={{ width: `${value}%` }}
            />
        </div>
    </div>
);

export const MetricsPanel: React.FC = () => {
    const metrics = useEventStore((state) => state.metrics);

    return (
        <div className="panel-container w-full h-full">
            <div className="panel-header">
                <div className="panel-title">
                    <Activity className="w-4 h-4" />
                    System Telemetry
                </div>
                <GripHorizontal className="w-4 h-4 text-gray-500 hover:text-cyan-vivid transition-colors cursor-grab active:cursor-grabbing" />
            </div>

            <div className="panel-content flex flex-col gap-6 pt-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-navy-800/50 p-3 rounded border border-cyan-vivid/10 flex flex-col items-center justify-center gap-1">
                        <span className="text-[10px] text-gray-500 uppercase tracking-widest">NET OUT</span>
                        <span className="text-lg font-mono text-cyan-vivid">{metrics.network.toFixed(0)} kb/s</span>
                    </div>
                    <div className="bg-navy-800/50 p-3 rounded border border-cyan-vivid/10 flex flex-col items-center justify-center gap-1">
                        <span className="text-[10px] text-gray-500 uppercase tracking-widest">THROUGHPUT</span>
                        <span className="text-lg font-mono text-violet-accent">{(metrics.cpu * 1.5).toFixed(0)} ops</span>
                    </div>
                </div>

                <div className="flex flex-col gap-5 mt-2">
                    <ProgressBar label="CPU Core Array" value={metrics.cpu} colorClass="text-cyan-vivid" />
                    <ProgressBar label="Neural Ram" value={metrics.ram} colorClass="text-electric-blue" />
                    <ProgressBar label="GPU Accelerator" value={metrics.gpu} colorClass="text-violet-accent" />
                </div>

                {/* Fake live chart area */}
                <div className="mt-auto h-24 w-full border-t border-cyan-vivid/10 pt-2 flex items-end gap-1 opacity-60">
                    {Array.from({ length: 20 }).map((_, i) => (
                        <div
                            key={i}
                            className="flex-1 bg-cyan-vivid/30 hover:bg-cyan-vivid/60 transition-colors rounded-t-sm"
                            style={{ height: `${Math.random() * 100}%` }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};
