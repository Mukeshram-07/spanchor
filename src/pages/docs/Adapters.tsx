import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Adapters: React.FC = () => {
  return (
    <DocumentationPage
      title="Adapters"
      description="Connect SPANCHOR to your search backend"
      route="/docs/adapters"
    >
      <section>
        <h2 id="what-are-adapters">What are Adapters?</h2>
        <p>
          Adapters are integration points that allow SPANCHOR to communicate with different 
          search backends and ranking systems. They abstract away backend-specific details.
        </p>
      </section>

      <section>
        <h2 id="supported-adapters">Supported Adapters</h2>
        <div className="space-y-4 my-4">
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">Elasticsearch</h3>
            <p className="text-sm text-text-secondary mt-1">Full-text and semantic search via BM25 and vector queries</p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">OpenSearch</h3>
            <p className="text-sm text-text-secondary mt-1">Amazon OpenSearch with neural search</p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">Weaviate</h3>
            <p className="text-sm text-text-secondary mt-1">Vector database with built-in ML modules</p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">LLM-based Reranker</h3>
            <p className="text-sm text-text-secondary mt-1">Use LLMs to rerank search results</p>
          </div>
        </div>
      </section>

      <section>
        <h2 id="elasticsearch-adapter">Elasticsearch Adapter</h2>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`from spanchor import SpanchorClient, Adapter

client = SpanchorClient(
    adapter=Adapter.elasticsearch,
    host="localhost",
    port=9200,
    index="documents"
)`}</code>
        </pre>
      </section>

      <section>
        <h2 id="custom-adapter">Custom Adapter</h2>
        <p>
          Implement a custom adapter for unsupported backends:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`from spanchor import BaseAdapter

class MySearchAdapter(BaseAdapter):
    def __init__(self, config):
        self.config = config
    
    def search(self, query, top_k=10):
        # Your search implementation
        results = self.my_search_engine.search(query, limit=top_k)
        return [doc.id for doc in results]
    
    def get_doc(self, doc_id):
        return self.my_search_engine.get(doc_id)

# Use custom adapter
client = SpanchorClient(adapter=MySearchAdapter(config))`}</code>
        </pre>
      </section>

      <section>
        <h2 id="adapter-configuration">Adapter Configuration</h2>
        <p>
          Each adapter accepts specific configuration parameters:
        </p>
        <ul>
          <li><strong>host</strong> - Search backend hostname</li>
          <li><strong>port</strong> - Backend port number</li>
          <li><strong>index</strong> - Index or collection name</li>
          <li><strong>embedding_model</strong> - Model for vector embeddings</li>
          <li><strong>auth</strong> - Authentication credentials</li>
        </ul>
      </section>

      <section>
        <h2 id="testing-adapters">Testing Your Adapter</h2>
        <p>
          Verify your adapter works before evaluating:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`# Test basic search
results = client.search("machine learning", top_k=5)
print(f"Found {len(results)} results")

# Test with gold set
metrics = client.evaluate(
    gold_set=gold_set['queries'][:5],  # Test with small subset
    top_k=10
)
print(f"Recall: {metrics.recall}")`}</code>
        </pre>
      </section>

      <section>
        <h2 id="adapter-performance">Performance Tuning</h2>
        <ul>
          <li>Use batch queries for large gold sets</li>
          <li>Cache embeddings for faster re-evaluation</li>
          <li>Configure timeouts appropriately</li>
          <li>Use connection pooling for backends</li>
          <li>Profile slow queries with your adapter</li>
        </ul>
      </section>
    </DocumentationPage>
  );
};

export default Adapters;
