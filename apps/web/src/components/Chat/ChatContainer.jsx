/**
 * Chat Container Component
 * Main chat interface with message list and input
 */

import { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage.jsx';
import { ChatInput } from './ChatInput.jsx';
import { ScrollToBottomButton } from '../UI/ScrollToBottomButton.jsx';
import { useChatStore } from '@/lib/state.js';
import { chatComplete } from '@/lib/api.js';

export function ChatContainer() {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const { messages, isLoading, addMessage, setLoading } = useChatStore();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text) => {
    // Add user message
    addMessage({
      role: 'user',
      content: text,
    });

    setLoading(true);

    try {
      // Call API
      const response = await chatComplete([
        ...messages.map(m => ({ role: m.role, content: m.content })),
        { role: 'user', content: text }
      ]);

      // Add assistant response
      addMessage({
        role: 'assistant',
        content: response.choices[0].message.content,
      });
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        role: 'assistant',
        content: `エラーが発生しました: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVoice = () => {
    // TODO: Implement voice input
    console.log('Voice input clicked');
  };

  const handleCamera = () => {
    // TODO: Implement camera
    console.log('Camera clicked');
  };

  const handleImage = () => {
    // TODO: Implement image upload
    console.log('Image upload clicked');
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Messages area with bottom padding to prevent content hiding behind fixed input */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto pb-48"
      >
        <div className="container mx-auto max-w-4xl px-4 py-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground py-12">
              <p className="text-lg">こんにちは！Oreza AIへようこそ。</p>
              <p className="text-sm mt-2">何かお手伝いできることはありますか？</p>
            </div>
          ) : (
            messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isUser={message.role === 'user'}
              />
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3 p-4 rounded-lg bg-muted/50">
              <div className="shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                <div className="animate-pulse">...</div>
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium">Oreza</div>
                <div className="text-sm text-muted-foreground">考え中...</div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll to bottom button */}
      <ScrollToBottomButton containerRef={containerRef} />

      {/* Fixed input at bottom */}
      <ChatInput
        onSend={handleSend}
        onVoice={handleVoice}
        onCamera={handleCamera}
        onImage={handleImage}
        disabled={isLoading}
      />
    </div>
  );
}
