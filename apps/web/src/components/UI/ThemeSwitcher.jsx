/**
 * Theme Switcher Component
 * Allows users to switch between Default and Midnight Journey themes
 */

import { Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu.jsx';
import { useSettingsStore } from '@/lib/state.js';
import { applyTheme, themes } from '@/lib/themes.js';

export function ThemeSwitcher() {
  const { theme, setTheme } = useSettingsStore();

  const handleThemeChange = (themeId) => {
    setTheme(themeId);
    applyTheme(themeId);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Switch theme">
          {theme === 'midnight' ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {Object.entries(themes).map(([id, themeData]) => (
          <DropdownMenuItem
            key={id}
            onClick={() => handleThemeChange(id)}
            className="cursor-pointer"
          >
            <div className="flex flex-col gap-1">
              <span className="font-medium">{themeData.name}</span>
              <span className="text-xs text-muted-foreground">
                {themeData.description}
              </span>
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
