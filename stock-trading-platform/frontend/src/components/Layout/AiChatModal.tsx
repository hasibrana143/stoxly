import React, { useState } from 'react';
import { usePersonalizedChatMutation } from '../../services/api';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface Props {
  open: boolean;
  onClose: () => void;
}

const AiChatModal: React.FC<Props> = ({ open, onClose }) => {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<{ role: 'user' | 'assistant'; text: string }[]>([]);
  const [personalizedChat, { isLoading }] = usePersonalizedChatMutation();

  if (!open) return null;

  const send = async () => {
    if (!message.trim()) return;
    setHistory((h) => [...h, { role: 'user', text: message }]);
    try {
      const res = await personalizedChat({ message, include_profile: true }).unwrap();
      setHistory((h) => [...h, { role: 'assistant', text: res.response }]);
    } catch (error: any) {
      let errorMsg = "Sorry, I encountered an error. Please try again.";
      if (error?.status === 401) {
        errorMsg = "Session expired. Please log out and log in again.";
      }
      setHistory((h) => [...h, { role: 'assistant', text: errorMsg }]);
    }
    setMessage('');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-end md:items-start justify-center md:justify-end p-4 z-50" onClick={onClose}>
      <div className="bg-white w-full max-w-full md:max-w-sm rounded-xl shadow-lg border" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-3 border-b">
          <div className="font-semibold">AI Assistant</div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="h-80 md:h-96 overflow-y-auto p-3 space-y-2">
          {history.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role === 'user' ? 'user' : 'bot'}`}>{m.text}</div>
          ))}

        </div>
        <div className="p-3 border-t flex space-x-2">
          <input
            id="ai-chat-message"
            name="message"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about stocks, ratios, peers..."
            className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={send}
            disabled={isLoading}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
        {/* Recommendations preview when available */}
        {/* This modal keeps UI lightweight; full details on Chat page */}
      </div>
    </div>
  );
};

export default AiChatModal;