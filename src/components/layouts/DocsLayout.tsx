import React from 'react';
import type { ReactNode } from 'react';
import Navbar from './Navbar';
import DocsSidebar from './DocsSidebar';
import Footer from './Footer';
import { cn } from '../../utils/cn';

interface TableOfContentsItem {
  id: string;
  title: string;
  level: number;
}

interface DocsLayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  tableOfContents?: TableOfContentsItem[];
}

const TableOfContents: React.FC<{ items: TableOfContentsItem[] }> = ({ items }) => {
  const [activeId, setActiveId] = React.useState<string>();

  React.useEffect(() => {
    if (items.length === 0) return;
    const handleScroll = () => {
      const headings = items.map(item => document.getElementById(item.id)).filter(Boolean);
      
      let current: Element | null = null;
      for (const heading of headings) {
        if (heading && heading.getBoundingClientRect().top < 100) {
          current = heading;
        } else {
          break;
        }
      }

      if (current) {
        const id = current.id;
        setActiveId(id);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [items]);

  return (
    <aside className="hidden lg:block w-64 flex-shrink-0 bg-primary-bg border-l border-border overflow-y-auto">
      <div className="sticky top-20 p-4">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-4">
          On this page
        </h3>
        <nav className="space-y-2 text-sm">
          {items.length === 0 ? (
            <p className="text-xs text-text-secondary">No items</p>
          ) : (
            items.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className={cn(
                  'block transition-colors hover:text-accent',
                  activeId === item.id
                    ? 'text-accent font-medium'
                    : 'text-text-secondary'
                )}
                style={{ paddingLeft: `${(item.level - 2) * 1}rem` }}
              >
                {item.title}
              </a>
            ))
          )}
        </nav>
      </div>
    </aside>
  );
};

const DocsLayout: React.FC<DocsLayoutProps> = ({
  children,
  title,
  description,
  tableOfContents = [],
}) => {

  return (
    <div className="min-h-screen flex flex-col bg-primary-bg">
      <Navbar />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <DocsSidebar onNavigate={() => window.scrollTo(0, 0)} />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            {(title || description) && (
              <header className="mb-8">
                {title && (
                  <h1 className="text-4xl font-bold text-text-primary mb-2">
                    {title}
                  </h1>
                )}
                {description && (
                  <p className="text-lg text-text-secondary">
                    {description}
                  </p>
                )}
              </header>
            )}

            {/* Content */}
            <article className="prose prose-invert max-w-none">
              {children}
            </article>

            {/* Navigation Footer */}
            <nav className="flex justify-between items-center mt-12 pt-8 border-t border-border">
              <div className="text-sm text-text-secondary">
                {/* Previous link can be added here */}
              </div>
              <div className="text-sm text-text-secondary">
                {/* Next link can be added here */}
              </div>
            </nav>
          </div>
        </main>

        {/* Table of Contents Sidebar */}
        <TableOfContents items={tableOfContents} />
      </div>

      <Footer />
    </div>
  );
};

export default DocsLayout;
