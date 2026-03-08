import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, Handle, Position } from 'reactflow';
import 'reactflow/dist/style.css';
import { useEventStore } from '../../store/eventStore';
import { Network, GripHorizontal } from 'lucide-react';

const CustomNode = ({ data }: any) => {
    const getBorderColor = () => {
        switch (data.status) {
            case 'active': return 'border-electric-blue drop-shadow-[0_0_8px_rgba(0,102,255,0.8)]';
            case 'completed': return 'border-cyan-vivid';
            case 'pending': return 'border-gray-600';
            case 'failed': return 'border-red-500';
            default: return 'border-gray-600';
        }
    };

    return (
        <div className={`bg-navy-800 p-3 rounded-md border text-xs font-mono min-w-[120px] text-center ${getBorderColor()} transition-all relative`}>
            <Handle type="target" position={Position.Left} className="w-1 h-3 rounded-none bg-cyan-vivid/50 border-none" />
            <span className={data.status === 'active' ? 'text-white font-bold' : 'text-gray-300'}>
                {data.label}
            </span>
            {data.status === 'active' && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-electric-blue rounded-full animate-ping" />
            )}
            <Handle type="source" position={Position.Right} className="w-1 h-3 rounded-none bg-cyan-vivid/50 border-none" />
        </div>
    );
};

const nodeTypes = {
    custom: CustomNode,
};

export const TaskGraphPanel: React.FC = () => {
    const tasks = useEventStore((state) => state.tasks);

    // Auto-layout simple horizontal for now
    const nodes = useMemo(() => {
        return tasks.nodes.map((node, i) => ({
            id: node.id,
            type: 'custom',
            position: { x: i * 200 + 50, y: 100 },
            data: { label: node.label, status: node.status }
        }));
    }, [tasks.nodes]);

    const edges = useMemo(() => {
        return tasks.edges.map(edge => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            animated: tasks.nodes.find(n => n.id === edge.source)?.status === 'active' || tasks.nodes.find(n => n.id === edge.target)?.status === 'active',
            style: { stroke: '#00f0ff', strokeWidth: 2 }
        }));
    }, [tasks.edges, tasks.nodes]);

    return (
        <div className="panel-container w-full h-full relative">
            <div className="panel-header absolute top-0 left-0 right-0 z-10 bg-navy-900/80 backdrop-blur-sm border-b-transparent">
                <div className="panel-title">
                    <Network className="w-4 h-4" />
                    Execution Graph
                </div>
                <GripHorizontal className="w-4 h-4 text-gray-500 hover:text-cyan-vivid transition-colors cursor-grab active:cursor-grabbing" />
            </div>

            <div className="w-full h-full pt-12">
                <div className="w-full h-full bg-navy-900/40 rounded-b-lg overflow-hidden">
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        nodeTypes={nodeTypes}
                        fitView
                        proOptions={{ hideAttribution: true }}
                    >
                        <Background gap={12} size={1} color="#00f0ff" className="opacity-10" />
                        <Controls className="!bg-navy-800 !border-cyan-vivid/20 !fill-white" showInteractive={false} />
                    </ReactFlow>
                </div>
            </div>
        </div>
    );
};
