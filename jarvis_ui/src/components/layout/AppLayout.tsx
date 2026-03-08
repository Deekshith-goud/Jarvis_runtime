import React, { useEffect } from 'react';
import { TopBar } from './TopBar';
import { BottomBar } from './BottomBar';
import { connectMockWebSocket } from '../../store/eventStore';

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    useEffect(() => {
        connectMockWebSocket();
    }, []);

    return (
        <div className="relative w-screen h-screen bg-navy-900 text-white overflow-hidden">
            <TopBar />

            {/* Background visualization layer */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                {/* 
                  Radial dark gradient on the actual background, 
                  but allowing the main content to shine. 
                 */}
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,theme(colors.cyan.900/0.05),transparent_60%)]"></div>
            </div>

            {/* Draggable Panels Layer */}
            <div className="absolute inset-0 pt-16 pb-28 px-4 z-10 pointer-events-none">
                <div className="w-full h-full pointer-events-auto">
                    {children}
                </div>
            </div>


            <BottomBar />
        </div >
    );
};
