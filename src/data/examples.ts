import type { Example } from '../types'

/**
 * Six example queries for semantic search demonstration
 */
export const EXAMPLES: Example[] = [
  {
    id: 'example-1',
    title: 'Information Retrieval',
    description: 'Find documents about search engine algorithms and ranking',
    query: 'How do search engines rank web pages?',
    results: [
      'PageRank algorithm overview',
      'Search engine ranking factors',
      'Information retrieval basics',
      'Web indexing techniques',
      'Relevance scoring methods',
    ],
  },
  {
    id: 'example-2',
    title: 'Natural Language Processing',
    description: 'Retrieve resources on text processing and understanding',
    query: 'Text processing and language models',
    results: [
      'Introduction to NLP',
      'Word embeddings and vectorization',
      'Semantic similarity measures',
      'Language model architectures',
      'Transformer models explained',
    ],
  },
  {
    id: 'example-3',
    title: 'Machine Learning',
    description: 'Discover ML papers and resources on optimization techniques',
    query: 'Deep learning optimization and training methods',
    results: [
      'Gradient descent variants',
      'Neural network training',
      'Loss function optimization',
      'Regularization techniques',
      'Hyperparameter tuning',
    ],
  },
  {
    id: 'example-4',
    title: 'Vector Databases',
    description: 'Resources on vector embeddings and similarity search',
    query: 'Vector similarity search and embeddings',
    results: [
      'Vector database systems',
      'Embedding techniques',
      'Similarity search algorithms',
      'Approximate nearest neighbor methods',
      'Vector indexing strategies',
    ],
  },
  {
    id: 'example-5',
    title: 'Semantic Web',
    description: 'Learn about semantic web technologies and knowledge graphs',
    query: 'Semantic web ontologies and knowledge representation',
    results: [
      'Ontology design principles',
      'Knowledge graphs',
      'Semantic reasoning',
      'Linked data standards',
      'RDF and semantic markup',
    ],
  },
  {
    id: 'example-6',
    title: 'Information Architecture',
    description: 'Understanding document organization and discovery',
    query: 'Document structure and metadata for better discovery',
    results: [
      'Information architecture principles',
      'Document metadata standards',
      'Content organization patterns',
      'Taxonomy design',
      'Search relevance modeling',
    ],
  },
]

/**
 * Get example by ID
 */
export const getExampleById = (id: string): Example | undefined => {
  return EXAMPLES.find((example) => example.id === id)
}

/**
 * Get all examples
 */
export const getAllExamples = (): Example[] => {
  return EXAMPLES
}

/**
 * Search examples by query
 */
export const searchExamples = (searchTerm: string): Example[] => {
  const term = searchTerm.toLowerCase()
  return EXAMPLES.filter(
    (example) =>
      example.title.toLowerCase().includes(term) ||
      example.description.toLowerCase().includes(term) ||
      example.query.toLowerCase().includes(term),
  )
}
