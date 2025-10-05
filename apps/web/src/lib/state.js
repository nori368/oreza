/**
 * Global state management using Zustand
 * Manages chat, image generation, and settings state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Chat state store
 */
export const useChatStore = create((set, get) => ({
  messages: [],
  isLoading: false,
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, { ...message, id: Date.now(), timestamp: new Date() }]
  })),
  
  updateLastMessage: (content) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0) {
      messages[messages.length - 1].content = content;
    }
    return { messages };
  }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  clearMessages: () => set({ messages: [] }),
}));

/**
 * Image generation state store
 */
export const useImageStore = create((set) => ({
  images: [],
  currentJobId: null,
  isGenerating: false,
  progress: 0,
  
  addImage: (image) => set((state) => ({
    images: [{ ...image, id: Date.now(), timestamp: new Date() }, ...state.images]
  })),
  
  setCurrentJob: (jobId) => set({ currentJobId: jobId }),
  
  setGenerating: (isGenerating) => set({ isGenerating }),
  
  setProgress: (progress) => set({ progress }),
  
  clearImages: () => set({ images: [] }),
}));

/**
 * Settings state store (persisted to localStorage)
 */
export const useSettingsStore = create(
  persist(
    (set) => ({
      theme: 'default',
      model: 'llama3.1:8b',
      searchProvider: 'tavily',
      mjMode: false,
      
      setTheme: (theme) => set({ theme }),
      setModel: (model) => set({ model }),
      setSearchProvider: (provider) => set({ searchProvider: provider }),
      setMjMode: (mjMode) => set({ mjMode }),
    }),
    {
      name: 'oreza-settings',
    }
  )
);

/**
 * UI state store
 */
export const useUIStore = create((set) => ({
  showScrollButton: false,
  currentMode: 'chat', // 'chat' | 'image' | 'search' | 'camera'
  sidebarOpen: false,
  
  setShowScrollButton: (show) => set({ showScrollButton: show }),
  setCurrentMode: (mode) => set({ currentMode: mode }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
