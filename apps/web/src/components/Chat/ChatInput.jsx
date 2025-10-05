/**
 * Chat Input Component
 * Fixed at bottom with proper spacing
 * Shift+Enter for newline, Enter for send
 */

import { useState, useRef } from 'react';
import { Send, Mic, Camera as CameraIcon, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';

export function ChatInput({ onSend, onVoice, onCamera, onImage, disabled = false }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  };

  return (
    <div className="sticky bottom-0 z-50 bg-background border-t border-border">
      {/* Safe area for mobile devices */}
      <div className="safe-area-inset-bottom">
        <div className="container mx-auto max-w-4xl px-4 py-4">
          <div className="flex items-end gap-2">
            {/* Action buttons with proper touch targets (44px minimum) */}
            <div className="flex gap-2 pb-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={onVoice}
                disabled={disabled}
                className="h-11 w-11 shrink-0"
                aria-label="Voice input"
              >
                <Mic className="h-5 w-5" />
              </Button>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={onCamera}
                disabled={disabled}
                className="h-11 w-11 shrink-0"
                aria-label="Camera"
              >
                <CameraIcon className="h-5 w-5" />
              </Button>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={onImage}
                disabled={disabled}
                className="h-11 w-11 shrink-0"
                aria-label="Upload image"
              >
                <ImageIcon className="h-5 w-5" />
              </Button>
            </div>

            {/* Text input area */}
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                placeholder="メッセージを入力... (Shift+Enterで改行、Enterで送信)"
                disabled={disabled}
                className="min-h-[44px] max-h-[200px] resize-none pr-12"
                rows={1}
              />
            </div>

            {/* Send button with proper spacing */}
            <Button
              onClick={handleSend}
              disabled={!input.trim() || disabled}
              size="icon"
              className="h-11 w-11 shrink-0 mb-0"
              aria-label="Send message"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          
          {/* Helper text */}
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Shift+Enterで改行、Enterで送信
          </p>
        </div>
      </div>
    </div>
  );
}
