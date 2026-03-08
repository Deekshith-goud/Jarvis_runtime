import { AppLayout } from './components/layout/AppLayout';
import { CoreSphereCanvas } from './components/sphere/CoreSphereCanvas';
import { DraggableGrid } from './components/panels/DraggableGrid';
import '/node_modules/react-grid-layout/css/styles.css';
import '/node_modules/react-resizable/css/styles.css';

function App() {
  return (
    <AppLayout>
      <div className="fixed inset-0 z-0 bg-transparent flex items-center justify-center pointer-events-none">
        <CoreSphereCanvas />
      </div>

      {/* Grid Layout will go here */}
      <div className="w-full h-full relative pointer-events-none z-10">
        <DraggableGrid />
      </div>
    </AppLayout>
  );
}

export default App;
