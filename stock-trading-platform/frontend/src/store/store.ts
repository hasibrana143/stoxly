import { configureStore } from '@reduxjs/toolkit';
import { stockApi } from '../services/api';
import authSlice from './authSlice';
import chatSlice from './chatSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    chat: chatSlice,
    [stockApi.reducerPath]: stockApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [stockApi.util.resetApiState.type],
      },
    }).concat(stockApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
