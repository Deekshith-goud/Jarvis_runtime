import { create } from 'zustand';

export type AgentStatus = 'idle' | 'running' | 'thinking' | 'completed';

export interface Agent {
    id: string;
    name: string;
    status: AgentStatus;
    currentTask?: string;
    progress?: number;
}

export interface TaskNode {
    id: string;
    label: string;
    status: 'pending' | 'active' | 'completed' | 'failed';
}

export interface TaskEdge {
    id: string;
    source: string;
    target: string;
}

export interface SystemMetrics {
    cpu: number;
    ram: number;
    network: number;
    gpu: number;
}

interface EventState {
    agents: Record<string, Agent>;
    metrics: SystemMetrics;
    tasks: {
        nodes: TaskNode[];
        edges: TaskEdge[];
    };
    isListening: boolean;
    addSystemLog: (log: string) => void;
    updateAgentStatus: (id: string, updates: Partial<Agent>) => void;
    updateMetrics: (metrics: Partial<SystemMetrics>) => void;
}

// Initial Mock State
const mockAgents: Record<string, Agent> = {
    'sys-1': { id: 'sys-1', name: 'SystemAgent', status: 'idle' },
    'brw-1': { id: 'brw-1', name: 'BrowserAgent', status: 'idle' },
    'rsr-1': { id: 'rsr-1', name: 'ResearchAgent', status: 'thinking', currentTask: 'Gathering data on AI frameworks' },
    'cod-1': { id: 'cod-1', name: 'CodeAgent', status: 'idle' },
    'prd-1': { id: 'prd-1', name: 'ProductivityAgent', status: 'idle' },
    'med-1': { id: 'med-1', name: 'MediaAgent', status: 'idle' },
};

export const useEventStore = create<EventState>((set) => ({
    agents: mockAgents,
    metrics: {
        cpu: 12,
        ram: 45,
        network: 5,
        gpu: 8
    },
    tasks: {
        nodes: [
            { id: '1', label: 'Command: Research', status: 'completed' },
            { id: '2', label: 'Planner', status: 'completed' },
            { id: '3', label: 'ResearchAgent', status: 'active' },
            { id: '4', label: 'Summarize', status: 'pending' }
        ],
        edges: [
            { id: 'e1-2', source: '1', target: '2' },
            { id: 'e2-3', source: '2', target: '3' },
            { id: 'e3-4', source: '3', target: '4' }
        ]
    },
    isListening: false,

    addSystemLog: () => set(() => {
        // In a real app we'd keep an array of logs
        return {};
    }),

    updateAgentStatus: (id, updates) => set((state) => ({
        agents: {
            ...state.agents,
            [id]: { ...state.agents[id], ...updates }
        }
    })),

    updateMetrics: (metrics) => set((state) => ({
        metrics: { ...state.metrics, ...metrics }
    }))
}));

// Mock WebSocket incoming events
export const connectMockWebSocket = () => {
    setInterval(() => {
        useEventStore.getState().updateMetrics({
            cpu: Math.max(5, Math.min(100, useEventStore.getState().metrics.cpu + (Math.random() * 10 - 5))),
            ram: Math.max(20, Math.min(100, useEventStore.getState().metrics.ram + (Math.random() * 2 - 1))),
            network: Math.random() * 100,
            gpu: Math.max(1, Math.min(100, useEventStore.getState().metrics.gpu + (Math.random() * 15 - 7)))
        });
    }, 2000);
};
