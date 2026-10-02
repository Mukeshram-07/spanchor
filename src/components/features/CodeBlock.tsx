    import React from 'react';
import CodeEditor from './CodeEditor';

interface CodeBlockProps {
  code?: string;
  language?: string;
  showLineNumbers?: boolean;
  showCopyButton?: boolean;
  showResetButton?: boolean;
  className?: string;
}

/**
 * CodeBlock Component
 *
 * Wrapper around CodeEditor for semantic naming.
 * Displays code with syntax highlighting and optional controls.
 */
const CodeBlock: React.FC<CodeBlockProps> = (props) => {
  return <CodeEditor {...props} />;
};

export default CodeBlock;
