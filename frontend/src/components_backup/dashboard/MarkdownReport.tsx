import React from 'react';

interface MarkdownReportProps {
  content: string;
}

export const MarkdownReport: React.FC<MarkdownReportProps> = ({ content }) => {
  return (
    <div className="prose prose-slate dark:prose-invert max-w-none">
      <pre className="whitespace-pre-wrap font-mono text-sm bg-slate-50 dark:bg-slate-800 p-4 rounded-lg">
        {content}
      </pre>
    </div>
  );
};
