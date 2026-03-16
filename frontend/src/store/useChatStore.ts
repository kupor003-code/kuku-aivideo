/*对话状态管理*/
import { create } from 'zustand';
import type { Message } from '../types';

interface ChatState {
  messages: Message[];
  sessionId: string | null;
  isLoading: boolean;
  suggestions: string[];

  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  setSessionId: (sessionId: string) => void;
  setLoading: (loading: boolean) => void;
  setSuggestions: (suggestions: string[]) => void;
  clear: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessionId: null,
  isLoading: false,
  suggestions: [],

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setMessages: (messages) => set({ messages }),

  setSessionId: (sessionId) => set({ sessionId }),

  setLoading: (isLoading) => set({ isLoading }),

  setSuggestions: (suggestions) => set({ suggestions }),

  clear: () =>
    set({
      messages: [],
      sessionId: null,
      isLoading: false,
      suggestions: [],
    }),
}));
