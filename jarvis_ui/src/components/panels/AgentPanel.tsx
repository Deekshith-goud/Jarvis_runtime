import React from 'react';
import { useEventStore } from '../../store/eventStore';
import { Bot, Cpu, CheckCircle2, Loader2, GripHorizontal } from 'lucide-react';

export const AgentPanel: React.FC = () => {
    const agents = useEventStore((state) => state.agents);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'running': return 'text-electric-blue drop-shadow-[0_0_8px_rgba(0,102,255,0.8)]';
            case 'thinking': return 'text-violet-accent animate-pulse drop-shadow-[0_0_8px_rgba(139,92,246,0.8)]';
            case 'completed': return 'text-cyan-vivid drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]';
            default: return 'text-gray-500';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'running': return <Loader2 className="w-4 h-4 animate-spin text-electric-blue" />;
            case 'thinking': return <Cpu className="w-4 h-4 animate-pulse text-violet-accent" />;
            case 'completed': return <CheckCircle2 className="w-4 h-4 text-cyan-vivid" />;
            default: return <div className="w-2 h-2 rounded-full bg-gray-500" />;
        }
    };

    return (
        <div className="panel-container w-full h-full">
            <div className="panel-header">
                <div className="panel-title">
                    <Bot className="w-4 h-4" />
                    Agent Swarm
                </div>
                <GripHorizontal className="w-4 h-4 text-gray-500 hover:text-cyan-vivid transition-colors cursor-grab active:cursor-grabbing" />
            </div>

            <div className="panel-content flex flex-col gap-3">
                {Object.values(agents).map(agent => (
                    <div key={agent.id} className="bg-navy-800/80 border border-cyan-vivid/10 rounded-lg p-3 flex flex-col gap-2 hover:border-cyan-vivid/30 transition-colors">
                        <div className="flex items-center justify-between">
                            <span className={`font-semibold text-sm ${getStatusColor(agent.status)} uppercase tracking-wider`}>
                                {agent.name}
                            </span>
                            {getStatusIcon(agent.status)}
                        </div>

                        {agent.currentTask && (
                            <div className="text-xs text-gray-400 truncate">
                                &gt; {agent.currentTask}
                            </div>
                        )}

                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] text-gray-500 uppercase tracking-widest">{agent.status}</span>
                            {agent.status !== 'idle' && agent.status !== 'completed' && (
                                <div className="h-1 flex-1 bg-navy-900 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${agent.status === 'thinking' ? 'bg-violet-accent' : 'bg-electric-blue'} animate-[pulse_2s_infinite] w-full origin-left`}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
