import React, { useState } from 'react';
import { Send, Mic } from 'lucide-react';
import { VoiceWaveform } from '../audio/VoiceWaveform';
import { useEventStore } from '../../store/eventStore';

export const BottomBar: React.FC = () => {
    const [inputVal, setInputVal] = useState('');
    const isListening = useEventStore((state) => state.isListening);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputVal.trim()) return;
        // Dispatch command
        console.log('Dispatching:', inputVal);
        setInputVal('');
    };

    return (
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-navy-900 via-navy-900/90 to-transparent flex flex-col justify-end pb-3 px-6 z-50 pointer-events-none">
            <div className="max-w-4xl mx-auto w-full relative flex items-center gap-3 pointer-events-auto">

                <VoiceWaveform active={isListening} />

                <form onSubmit={handleSubmit} className="relative flex-1 flex items-center group">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-cyan-vivid font-mono text-sm">&gt;</span>
                    </div>
                    <input
                        type="text"
                        className="w-full bg-navy-800/60 border border-cyan-vivid/30 text-white rounded-md pl-8 pr-10 py-1.5 focus:outline-none focus:border-cyan-vivid focus:ring-1 focus:ring-cyan-vivid/50 transition-all font-mono text-sm placeholder-gray-500 backdrop-blur-md"
                        placeholder="Awaiting command..."
                        value={inputVal}
                        onChange={(e) => setInputVal(e.target.value)}
                    />
                    <button
                        type="button"
                        className="absolute inset-y-0 right-8 pr-2 flex items-center text-gray-400 hover:text-cyan-vivid transition-colors"
                    >
                        <Mic className="w-4 h-4" />
                    </button>
                    <button
                        type="submit"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-cyan-vivid transition-colors"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </form>
                {/* Glow effect behind the input */}
                <div className="absolute inset-0 -z-10 bg-cyan-vivid/5 blur-lg group-focus-within:bg-cyan-vivid/10 transition-colors pointer-events-none rounded-md"></div>
            </div>
        </div>
    );
};
