import React, { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import DocsLayout from '../layouts/DocsLayout';

interface TableOfContentsItem {
  id: string;
  title: string;
  level: number;
}

interface DocumentationPageProps {
  title: string;
  description?: string;
  children: ReactNode;
  route?: string;
}

/**
 * Extract headings from rendered content to build table of contents
 */
const extractHeadings = (container: HTMLElement | null): TableOfContentsItem[] => {
  if (!container) return [];

  const headings = container.querySelectorAll('h2, h3');
  const items: TableOfContentsItem[] = [];

  headings.forEach((heading, index) => {
    // Ensure heading has an ID
    if (!heading.id) {
      heading.id = `heading-${index}`;
    }

    const level = parseInt(heading.tagName[1]);
    items.push({
      id: heading.id,
      title: heading.textContent || '',
      level,
    });
  });

  return items;
};

const DocumentationPage: React.FC<DocumentationPageProps> = ({
  title,
  description,
  children,
}) => {
  const [tableOfContents, setTableOfContents] = useState<TableOfContentsItem[]>([]);
  const contentRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Small delay to ensure content is rendered
    const timer = setTimeout(() => {
      if (contentRef.current) {
        const headings = extractHeadings(contentRef.current);
        setTableOfContents(headings);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [children]);

  return (
    <DocsLayout title={title} description={description} tableOfContents={tableOfContents}>
      <div ref={contentRef} className="space-y-6">
        {children}
      </div>
    </DocsLayout>
  );
};

export default DocumentationPage;
