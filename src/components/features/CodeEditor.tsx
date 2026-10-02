import React, { useState, useRef } from 'react';
import { Copy, RotateCcw, Check } from 'lucide-react';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-light.css';
import { cn } from '../../utils/cn';

interface CodeEditorProps {
  code?: string;
  language?: string;
  filename?: string;
  showLineNumbers?: boolean;
  showCopyButton?: boolean;
  showResetButton?: boolean;
  className?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  code = `from spanchor import evaluate

result = evaluate(
    queries=queries,
    retrieved=retrieved,
    gold=gold,
)
print(result)`,
  language = 'python',
  filename,
  showLineNumbers = true,
  showCopyButton = true,
  showResetButton = true,
  className,
}) => {
  const [copiedText, setCopiedText] = useState(false);
  const [currentCode, setCurrentCode] = useState(code);
  const codeRef = useRef<HTMLPreElement>(null);

  const highlightCode = (codeToHighlight: string) => {
    try {
      return hljs.highlight(codeToHighlight, { language }).value;
    } catch {
      // Fallback to plain text if language not recognized
      return hljs.highlightAuto(codeToHighlight).value;
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(currentCode);
      setCopiedText(true);
      setTimeout(() => setCopiedText(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleReset = () => {
    setCurrentCode(code);
  };

  const lines = currentCode.split('\n');

  // Determine display filename
  const displayFilename = filename || (language === 'shell' ? 'Shell' : `${language.charAt(0).toUpperCase() + language.slice(1)}`);

  return (
    <div
      className={cn(
        'rounded-lg overflow-hidden border',
        'border-slate-200',
        className
      )}
      style={{
        backgroundColor: '#F8FAFC',
        borderTop: '3px solid #0284C7',
      }}
    >
      {/* Header with Filename and Actions */}
      <div
        className="border-b border-slate-200 px-4 py-3 flex items-center justify-between"
        style={{
          backgroundColor: '#F1F5F9',
        }}
      >
        <span className="text-xs font-mono font-semibold text-slate-700">
          {displayFilename}
        </span>
        <div className="flex items-center gap-2">
          {showResetButton && (
            <button
              onClick={handleReset}
              className="p-1.5 rounded transition-all hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-0"
              aria-label="Reset code"
              title="Reset code"
            >
              <RotateCcw className="w-4 h-4 text-slate-600" />
            </button>
          )}
          {showCopyButton && (
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono font-medium transition-all hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-0"
              aria-label={copiedText ? 'Copied to clipboard' : 'Copy code to clipboard'}
              title={copiedText ? 'Copied!' : 'Copy code'}
            >
              {copiedText ? (
                <>
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span className="text-emerald-600">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 text-slate-600" />
                  <span className="text-slate-600">Copy</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Code Display */}
      <pre
        ref={codeRef}
        className="p-4 overflow-x-auto"
        style={{
          backgroundColor: '#F8FAFC',
          color: '#1E293B',
          fontFamily: "'Monaco', 'Menlo', 'Ubuntu Mono', 'Courier New', monospace",
          fontSize: '13px',
          lineHeight: '1.6',
        }}
        role="region"
        aria-label={`Code example in ${language}`}
      >
        <code>
          {showLineNumbers ? (
            <div className="flex">
              {/* Line Numbers Column */}
              <div
                className="select-none pr-4 text-right"
                style={{
                  minWidth: '3rem',
                  color: '#94A3B8',
                  borderRight: '1px solid #E2E8F0',
                }}
              >
                {lines.map((_, index) => (
                  <div key={index} className="leading-6">
                    {index + 1}
                  </div>
                ))}
              </div>

              {/* Code Column */}
              <div className="pl-4 flex-1">
                <div
                  dangerouslySetInnerHTML={{
                    __html: highlightCode(currentCode),
                  }}
                />
              </div>
            </div>
          ) : (
            <div
              dangerouslySetInnerHTML={{
                __html: highlightCode(currentCode),
              }}
            />
          )}
        </code>
      </pre>
    </div>
  );
};

export default CodeEditor;
