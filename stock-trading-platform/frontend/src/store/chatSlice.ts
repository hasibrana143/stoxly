import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChatMessage {
  id: string;
  message: string;
  isUser: boolean;
  timestamp: string;
}

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
}

const initialState: ChatState = {
  messages: [
    {
      id: '1',
      message: 'Hello! I\'m your AI stock advisor. How can I help you with your investments today?',
      isUser: false,
      timestamp: new Date().toISOString(),
    },
  ],
  isLoading: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Omit<ChatMessage, 'id'>>) => {
      const message: ChatMessage = {
        ...action.payload,
        id: Math.random().toString(36).substr(2, 9),
      };
      state.messages.push(message);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [
        {
          id: '1',
          message: 'Hello! I\'m your AI stock advisor. How can I help you with your investments today?',
          isUser: false,
          timestamp: new Date().toISOString(),
        },
      ];
    },
    addUserMessage: (state, action: PayloadAction<string>) => {
      const message: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        message: action.payload,
        isUser: true,
        timestamp: new Date().toISOString(),
      };
      state.messages.push(message);
    },
    addBotMessage: (state, action: PayloadAction<string>) => {
      const message: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        message: action.payload,
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      state.messages.push(message);
    },
  },
});

export const {
  addMessage,
  setLoading,
  clearMessages,
  addUserMessage,
  addBotMessage,
} = chatSlice.actions;

export default chatSlice.reducer;
