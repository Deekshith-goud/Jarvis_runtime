import React from 'react';
import { useEventStore } from '../../store/eventStore';
import { Activity, Database, Server, Volume2 } from 'lucide-react';

export const TopBar: React.FC = () => {
    const isListening = useEventStore((state) => state.isListening);

    return (
        <div className="absolute top-0 left-0 right-0 h-10 bg-navy-900/80 backdrop-blur-md border-b border-cyan-vivid/20 flex items-center justify-between px-4 z-50">
            <div className="flex items-center gap-3">
                <Server className="w-4 h-4 text-cyan-vivid animate-pulse" />
                <h1 className="text-base font-bold text-white tracking-widest flex items-center gap-2">
                    JARVIS
                    <span className="text-[10px] text-cyan-vivid/70 border border-cyan-vivid/30 px-1.5 rounded-full ml-1">v2</span>
                </h1>
            </div>

            <div className="flex space-x-5 text-xs">
                <div className="flex items-center gap-1.5 text-gray-300">
                    <Database className="w-3.5 h-3.5 text-violet-accent" />
                    <span>Memory: Syncing</span>
                </div>
                <div className="flex items-center gap-1.5 text-gray-300">
                    <Activity className="w-3.5 h-3.5 text-electric-blue" />
                    <span>Status: Optimal</span>
                </div>
                <div className="flex items-center gap-1.5 text-gray-300">
                    <Volume2 className={`w-3.5 h-3.5 ${isListening ? 'text-cyan-vivid animate-pulse' : 'text-gray-500'}`} />
                    <span>Audio: {isListening ? 'Listening' : 'Ready'}</span>
                </div>
            </div>
        </div>
    );
};
