import React from 'react';

interface MessageProps {
  content: string;
  isUser: boolean;
  timestamp: Date;
}

const Message: React.FC<MessageProps> = ({ content, isUser, timestamp }) => {
  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}
    >
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-tactical-navy text-tactical-e-ink'
            : 'bg-tactical-slate-medium text-tactical-e-ink border border-tactical-slate-light/20'
        } shadow-md`}
      >
        <p className="text-sm whitespace-pre-wrap">{content}</p>
        <p className="text-xs mt-1 opacity-70">
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};

export default Message;
