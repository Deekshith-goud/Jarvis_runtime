import { create } from 'zustand';

interface LayoutState {
    isTaskGraphVisible: boolean;
    isMemoryVisible: boolean;
    isAutomationVisible: boolean;
    toggleTaskGraph: () => void;
    toggleMemory: () => void;
    toggleAutomation: () => void;
}

export const useUIStore = create<LayoutState>((set) => ({
    isTaskGraphVisible: false,
    isMemoryVisible: false,
    isAutomationVisible: false,

    toggleTaskGraph: () => set((state) => ({ isTaskGraphVisible: !state.isTaskGraphVisible })),
    toggleMemory: () => set((state) => ({ isMemoryVisible: !state.isMemoryVisible })),
    toggleAutomation: () => set((state) => ({ isAutomationVisible: !state.isAutomationVisible })),
}));
