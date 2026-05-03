import React, { useMemo } from 'react';
import { marked } from 'marked';

marked.setOptions({ gfm: true, breaks: false });

type Props = {
  content: string;
  className?: string;
};

export function MarkdownRenderer({ content, className }: Props): React.JSX.Element {
  const html = useMemo(() => marked.parse(content, { async: false }) as string, [content]);
  return (
    <div
      className={`prose${className ? ` ${className}` : ''}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
