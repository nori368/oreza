/**
 * Header Component
 * Top navigation bar with mode switcher and theme toggle
 */

import { MessageSquare, Image, Search, Camera, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { ThemeSwitcher } from './ThemeSwitcher.jsx';
import { useUIStore } from '@/lib/state.js';
import { cn } from '@/lib/utils.js';

const modes = [
  { id: 'chat', label: 'チャット', icon: MessageSquare },
  { id: 'image', label: '画像生成', icon: Image },
  { id: 'search', label: 'Web検索', icon: Search },
  { id: 'camera', label: 'カメラ', icon: Camera },
];

export function Header() {
  const { currentMode, setCurrentMode } = useUIStore();

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold">Oreza AI</h1>
        </div>

        {/* Mode Switcher */}
        <nav className="flex items-center gap-1">
          {modes.map((mode) => {
            const Icon = mode.icon;
            return (
              <Button
                key={mode.id}
                variant={currentMode === mode.id ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentMode(mode.id)}
                className={cn(
                  "gap-2",
                  currentMode === mode.id && "shadow-sm"
                )}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{mode.label}</span>
              </Button>
            );
          })}
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <ThemeSwitcher />
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
