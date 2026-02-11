import React, { useState, useRef, useEffect } from 'react';
import { X, Send, MessageCircle } from 'lucide-react';
import Message from './Message';

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: '👋 Hi there! I\'m Nextier\'s AI Agent. How can I help you today?',
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const botResponse = `👋 Hi there! I'm Nextier's AI Agent, your future companion for navigating conflict and violence data across Nigeria.

I'm currently in development and will soon be able to help you:
✨ Query specific incidents and trends
📊 Generate custom reports and insights
🗺️ Explore geographic patterns
📈 Analyze temporal data

Stay tuned—something powerful is coming! 🚀`;

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate bot typing delay
    setTimeout(() => {
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: botResponse,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 lg:hidden">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-lg h-[600px] flex flex-col animate-slide-up">
        {/* Mobile Header */}
        <div className="flex items-center justify-between p-4 border-b border-tactical-slate-light/20 bg-tactical-navy">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-tactical-e-ink" />
            <h3 className="font-semibold text-tactical-e-ink">Nextier AI Agent</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-tactical-slate-medium/20 rounded transition-colors"
          >
            <X className="w-5 h-5 text-tactical-e-ink" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-tactical-e-ink">
          {messages.map(message => (
            <Message key={message.id} {...message} />
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-tactical-slate-medium text-tactical-e-ink px-4 py-3 rounded-lg border border-tactical-slate-light/20">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-tactical-e-ink rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-tactical-e-ink rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-tactical-e-ink rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-tactical-slate-light/20 bg-white">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-tactical-slate-light/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-tactical-navy focus:border-transparent"
              disabled={isTyping}
            />
            <button
              onClick={handleSendMessage}
              disabled={isTyping || inputValue.trim() === ''}
              className="px-4 py-2 bg-tactical-navy text-tactical-e-ink rounded-lg hover:bg-tactical-charcoal transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
