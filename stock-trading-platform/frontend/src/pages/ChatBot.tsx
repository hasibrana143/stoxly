import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { usePersonalizedChatMutation } from '../services/api';
import { addUserMessage, addBotMessage } from '../store/chatSlice';

const ChatBot: React.FC = () => {
  const [message, setMessage] = useState('');
  const [personalizedChat, { isLoading }] = usePersonalizedChatMutation();
  const [recommendations, setRecommendations] = useState<{
    stock_symbol: string;
    recommendation_type: string;
    confidence_score?: number;
    reason?: string;
    target_price?: number;
  }[] | null>(null);
  const messages = useAppSelector((state) => state.chat.messages);
  const dispatch = useAppDispatch();

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    dispatch(addUserMessage(message));
    const userMessage = message;
    setMessage('');

    try {
      const result = await personalizedChat({ message: userMessage, include_profile: true }).unwrap();
      dispatch(addBotMessage(result.response));
      setRecommendations(result.recommendations || null);
    } catch (error) {
      dispatch(addBotMessage('Sorry, I encountered an error. Please try again.'));
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">AI Stock Advisor</h1>
      
      <div className="card min-h-[24rem] flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`chat-bubble ${msg.isUser ? 'user' : 'bot'}`}>
                {msg.message}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="chat-bubble bot">
                <span className="loading-spinner mr-2"></span>
                Thinking...
              </div>
            </div>
          )}
          {recommendations && recommendations.length > 0 && (
            <div className="mt-4">
              <div className="text-sm font-semibold text-gray-900 mb-2">Personalized Recommendations</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-md">
                    <div className="text-sm font-medium text-gray-900">{rec.stock_symbol} — {rec.recommendation_type.toUpperCase()}</div>
                    {rec.reason && <div className="text-xs text-gray-700 mt-1">{rec.reason}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <form onSubmit={handleSendMessage} className="border-t p-4">
          <div className="flex gap-4">
            <input
              id="chat-message"
              name="message"
              type="text"
              className="flex-1 input-field"
              placeholder="Ask about stocks, market trends, or investment advice..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="btn-primary"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatBot;
