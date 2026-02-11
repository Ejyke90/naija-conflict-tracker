import React, { useState } from 'react';
import { MessageCircle, X, Send, Bot } from 'lucide-react';
import ChatPanel from './ChatPanel';

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatWidget: React.FC = () => {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
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
  const [showDesktopChat, setShowDesktopChat] = useState(false);

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

  return (
    <>
      {/* Desktop Chat Widget */}
      <div className="hidden lg:block fixed bottom-6 right-6 z-40">
        {showDesktopChat ? (
          <div className="w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-tactical-slate-light/20 flex flex-col animate-slide-up">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-tactical-slate-light/20 bg-tactical-navy">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-tactical-e-ink" />
                <h3 className="font-semibold text-tactical-e-ink">Nextier AI Agent</h3>
              </div>
              <button
                onClick={() => setShowDesktopChat(false)}
                className="p-1 hover:bg-tactical-slate-medium/20 rounded transition-colors"
              >
                <X className="w-5 h-5 text-tactical-e-ink" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-tactical-e-ink">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
                >
                  <div
                    className={`max-w-xs px-4 py-3 rounded-lg ${
                      message.isUser
                        ? 'bg-tactical-navy text-tactical-e-ink'
                        : 'bg-tactical-slate-medium text-tactical-e-ink border border-tactical-slate-light/20'
                    } shadow-md`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
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
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Floating Chat Button */
          <button
            onClick={() => setShowDesktopChat(true)}
            className="w-14 h-14 bg-tactical-navy text-tactical-e-ink rounded-full shadow-lg hover:bg-tactical-charcoal transition-all duration-200 hover:scale-110 flex items-center justify-center border border-tactical-slate-light/30"
          >
            <MessageCircle className="w-6 h-6" />
          </button>
        )}
      </div>

      {/* Mobile Chat Button */}
      <div className="lg:hidden fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsPanelOpen(true)}
          className="w-14 h-14 bg-tactical-navy text-tactical-e-ink rounded-full shadow-lg hover:bg-tactical-charcoal transition-all duration-200 hover:scale-110 flex items-center justify-center border border-tactical-slate-light/30"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      </div>

      {/* Mobile Chat Panel */}
      <ChatPanel isOpen={isPanelOpen} onClose={() => setIsPanelOpen(false)} />

      <style jsx>{`
        @keyframes slide-up {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }

        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default ChatWidget;
