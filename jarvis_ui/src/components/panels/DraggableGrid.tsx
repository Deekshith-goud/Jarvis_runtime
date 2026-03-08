// @ts-nocheck
import React, { useMemo, useState, useEffect, useRef } from 'react';
import { Responsive } from 'react-grid-layout';
import { AgentPanel } from './AgentPanel';
import { MetricsPanel } from './MetricsPanel';
import { TaskGraphPanel } from './TaskGraphPanel';

export const DraggableGrid: React.FC = () => {
    const [width, setWidth] = useState(1200);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        const observer = new ResizeObserver((entries) => {
            if (entries[0]) setWidth(entries[0].contentRect.width);
        });
        observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    const layouts = useMemo(() => {
        return {
            lg: [
                { i: 'agents', x: 0, y: 0, w: 3, h: 4 },
                { i: 'metrics', x: 9, y: 0, w: 3, h: 4 },
                { i: 'graph', x: 8, y: 4, w: 4, h: 5 },
            ],
            md: [
                { i: 'agents', x: 0, y: 0, w: 3, h: 4 },
                { i: 'metrics', x: 7, y: 0, w: 3, h: 4 },
                { i: 'graph', x: 6, y: 4, w: 4, h: 4 },
            ],
            sm: [
                { i: 'agents', x: 0, y: 0, w: 6, h: 4 },
                { i: 'metrics', x: 0, y: 4, w: 6, h: 4 },
                { i: 'graph', x: 0, y: 8, w: 6, h: 4 },
            ]
        };
    }, []);

    return (
        <div ref={containerRef} className="w-full h-full pt-4">
            {/* @ts-ignore */}
            <Responsive
                className="layout pointer-events-auto w-full h-full"
                width={width || 1200}
                layouts={layouts}
                breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
                cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
                rowHeight={50}
                draggableHandle=".panel-header"
                isResizable={true}
                margin={[12, 12]} // Spacing between panels
                compactType={null} // Allow free floating
                preventCollision={false}
            >
                <div key="agents">
                    <AgentPanel />
                </div>
                <div key="metrics">
                    <MetricsPanel />
                </div>
                <div key="graph">
                    <TaskGraphPanel />
                </div>
            </Responsive>
        </div>
    );
};
