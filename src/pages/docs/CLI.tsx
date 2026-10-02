import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const CLI: React.FC = () => {
  return (
    <DocumentationPage
      title="Command Line Interface (CLI)"
      description="Use SPANCHOR from the command line"
      route="/docs/cli"
    >
      <section>
        <h2 id="overview">Overview</h2>
        <p>
          The SPANCHOR CLI allows you to run tests, evaluate gold sets, and manage configurations 
          from the command line without writing Python code.
        </p>
      </section>

      <section>
        <h2 id="installation-cli">Installation</h2>
        <p>
          The CLI is included with SPANCHOR:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>pip install spanchor</code>
        </pre>
      </section>

      <section>
        <h2 id="basic-commands">Basic Commands</h2>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`# Show help
spanchor --help

# Evaluate a gold set
spanchor evaluate --gold-set gold_set.json --adapter elasticsearch

# Compare two configurations
spanchor compare --baseline baseline.json --candidate candidate.json

# Show version
spanchor --version`}</code>
        </pre>
      </section>

      <section>
        <h2 id="evaluate-command">Evaluate Command</h2>
        <p>
          Evaluate a gold set against your search backend:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`spanchor evaluate \\
  --gold-set gold_set.json \\
  --adapter elasticsearch \\
  --host localhost \\
  --port 9200 \\
  --index documents \\
  --top-k 10 \\
  --output results.json`}</code>
        </pre>
      </section>

      <section>
        <h2 id="compare-command">Compare Command</h2>
        <p>
          Compare evaluation results:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`spanchor compare \\
  --baseline baseline_results.json \\
  --candidate candidate_results.json \\
  --output comparison.json`}</code>
        </pre>
      </section>

      <section>
        <h2 id="config-command">Config Command</h2>
        <p>
          Manage configurations:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`# Create a configuration file
spanchor config create --name prod --adapter elasticsearch

# List configurations
spanchor config list

# Show a configuration
spanchor config show prod`}</code>
        </pre>
      </section>

      <section>
        <h2 id="options">Common Options</h2>
        <ul>
          <li><code>--verbose</code> - Increase output verbosity</li>
          <li><code>--quiet</code> - Suppress output</li>
          <li><code>--output</code> - Output file path</li>
          <li><code>--format</code> - Output format (json, csv, table)</li>
          <li><code>--config</code> - Configuration file</li>
        </ul>
      </section>

      <section>
        <h2 id="exit-codes">Exit Codes</h2>
        <ul>
          <li><code>0</code> - Success</li>
          <li><code>1</code> - General error</li>
          <li><code>2</code> - Command line argument error</li>
          <li><code>3</code> - Configuration error</li>
        </ul>
      </section>

      <section>
        <h2 id="examples">Examples</h2>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`# Quick evaluation
spanchor evaluate --gold-set gold_set.json --adapter elasticsearch

# Full workflow
spanchor evaluate --gold-set gold_set.json \\
  --adapter elasticsearch --output baseline.json
spanchor evaluate --gold-set gold_set.json \\
  --adapter elasticsearch --config prod --output candidate.json
spanchor compare --baseline baseline.json --candidate candidate.json`}</code>
        </pre>
      </section>
    </DocumentationPage>
  );
};

export default CLI;
