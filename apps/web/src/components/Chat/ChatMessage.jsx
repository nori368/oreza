/**
 * Chat Message Component
 * Displays individual chat messages with proper styling
 */

import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils.js';

export function ChatMessage({ message, isUser = false }) {
  return (
    <div className={cn(
      "flex gap-3 p-4 rounded-lg",
      isUser ? "bg-primary/10" : "bg-muted/50"
    )}>
      {/* Avatar */}
      <div className={cn(
        "shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
      )}>
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message content */}
      <div className="flex-1 space-y-2">
        <div className="text-sm font-medium">
          {isUser ? 'あなた' : 'Oreza'}
        </div>
        <div className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </div>
        {message.timestamp && (
          <div className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString('ja-JP')}
          </div>
        )}
      </div>
    </div>
  );
}
