import { useEffect } from 'react';
import { Header } from '@/components/UI/Header.jsx';
import { ChatContainer } from '@/components/Chat/ChatContainer.jsx';
import { ImageGenerator } from '@/components/ImageGen/ImageGenerator.jsx';
import { ImageGallery } from '@/components/ImageGen/ImageGallery.jsx';
import { useUIStore, useSettingsStore } from '@/lib/state.js';
import { applyTheme, getCurrentTheme } from '@/lib/themes.js';
import './App.css';

function App() {
  const { currentMode } = useUIStore();
  const { theme } = useSettingsStore();

  // Apply theme on mount
  useEffect(() => {
    const savedTheme = getCurrentTheme();
    applyTheme(savedTheme.id);
  }, []);

  // Apply theme when it changes
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      
      <main className="h-[calc(100vh-4rem)]">
        {currentMode === 'chat' && <ChatContainer />}
        
        {currentMode === 'image' && (
          <div className="h-full overflow-y-auto">
            <ImageGenerator />
            <ImageGallery />
          </div>
        )}
        
        {currentMode === 'search' && (
          <div className="container mx-auto max-w-4xl px-4 py-12 text-center">
            <h2 className="text-2xl font-bold mb-4">Web検索</h2>
            <p className="text-muted-foreground">準備中...</p>
          </div>
        )}
        
        {currentMode === 'camera' && (
          <div className="container mx-auto max-w-4xl px-4 py-12 text-center">
            <h2 className="text-2xl font-bold mb-4">カメラ</h2>
            <p className="text-muted-foreground">準備中...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
