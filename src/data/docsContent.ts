import type { DocsPage, DocSection } from '../types'

/**
 * Documentation pages
 */
export const DOCS_PAGES: DocsPage[] = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    content: 'Learn the basics of Spanchor and how to integrate semantic search into your application.',
    sections: [
      {
        id: 'intro',
        title: 'Introduction',
        content:
          'Spanchor is a semantic search and ranking optimization platform designed for developers who want to build intelligent search experiences. It provides APIs for semantic search, re-ranking, and evaluation of search quality.',
      },
      {
        id: 'installation',
        title: 'Installation',
        content:
          'To get started with Spanchor, you can install the client library via npm:\n\nnpm install @spanchor/client\n\nThen, import and initialize the client in your application.',
      },
      {
        id: 'first-search',
        title: 'Your First Search',
        content:
          'Here\'s a simple example of performing a semantic search query using Spanchor:\n\n```typescript\nconst results = await spanchor.search("machine learning algorithms");\nconsole.log(results);\n```',
      },
    ],
  },
  {
    id: 'core-concepts',
    title: 'Core Concepts',
    content: 'Understand the fundamental concepts behind semantic search and ranking.',
    sections: [
      {
        id: 'semantic-search',
        title: 'Semantic Search',
        content:
          'Semantic search goes beyond simple keyword matching. It understands the meaning and intent behind a query and finds documents with similar semantic meaning. This is powered by neural embedding models.',
      },
      {
        id: 'embeddings',
        title: 'Embeddings',
        content:
          'Embeddings are numerical representations of text that capture semantic meaning. Documents and queries are converted to embeddings, which are then compared to find the most relevant matches.',
      },
      {
        id: 'ranking',
        title: 'Ranking',
        content:
          'Ranking is the process of ordering search results by relevance. Spanchor provides both retrieval-based and learned-to-rank models for optimizing ranking quality.',
      },
      {
        id: 'evaluation',
        title: 'Evaluation Metrics',
        content:
          'Search quality is measured using metrics like Recall@K (what percentage of relevant documents were retrieved), Precision@K (what percentage of retrieved documents are relevant), and Hit Rate.',
      },
    ],
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    content: 'Complete reference documentation for all Spanchor APIs.',
    sections: [
      {
        id: 'authentication',
        title: 'Authentication',
        content:
          'To use the Spanchor API, you need to authenticate with an API key. Include your API key in the Authorization header:\n\nAuthorization: Bearer YOUR_API_KEY',
      },
      {
        id: 'rate-limiting',
        title: 'Rate Limiting',
        content:
          'API requests are rate limited to 100 requests per minute per API key. If you exceed this limit, you\'ll receive a 429 status code.',
      },
      {
        id: 'error-handling',
        title: 'Error Handling',
        content:
          'The API uses standard HTTP status codes. Errors are returned in JSON format with a "message" field explaining the issue.',
      },
    ],
  },
  {
    id: 'best-practices',
    title: 'Best Practices',
    content: 'Tips and best practices for getting the most out of Spanchor.',
    sections: [
      {
        id: 'query-optimization',
        title: 'Query Optimization',
        content:
          'Write clear, specific queries for better results. Avoid overly broad queries and use domain-specific terminology when appropriate.',
      },
      {
        id: 'data-preparation',
        title: 'Data Preparation',
        content:
          'Ensure your documents are well-structured with clear titles, descriptions, and metadata. This helps improve search quality significantly.',
      },
      {
        id: 'benchmarking',
        title: 'Benchmarking',
        content:
          'Always evaluate your search implementation against a representative benchmark dataset to ensure it meets your quality requirements.',
      },
    ],
  },
]

/**
 * Get docs page by ID
 */
export const getDocsPageById = (id: string): DocsPage | undefined => {
  return DOCS_PAGES.find((page) => page.id === id)
}

/**
 * Get all docs pages
 */
export const getAllDocsPages = (): DocsPage[] => {
  return DOCS_PAGES
}

/**
 * Get docs section within a page
 */
export const getDocsSectionById = (pageId: string, sectionId: string): DocSection | undefined => {
  const page = getDocsPageById(pageId)
  return page?.sections.find((section) => section.id === sectionId)
}
