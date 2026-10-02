import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Installation: React.FC = () => {
  return (
    <DocumentationPage
      title="Installation"
      description="Get SPANCHOR up and running in your project"
      route="/docs/installation"
    >
      <section>
        <h2 id="requirements">Requirements</h2>
        <ul>
          <li>Python 3.8 or higher</li>
          <li>pip package manager</li>
          <li>Access to your search backend or embedding model API</li>
        </ul>
      </section>

      <section>
        <h2 id="install-from-pypi">Install from PyPI</h2>
        <p>
          The recommended way to install SPANCHOR is via pip:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>pip install spanchor</code>
        </pre>
      </section>

      <section>
        <h2 id="verify-installation">Verify Installation</h2>
        <p>
          After installation, verify it worked by importing SPANCHOR in Python:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`python -c "import spanchor; print(spanchor.__version__)"`}</code>
        </pre>
      </section>

      <section>
        <h2 id="install-from-source">Install from Source</h2>
        <p>
          For development or to use the latest code:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`git clone https://github.com/Mukeshram-07/spanchor.git
cd spanchor
pip install -e .`}</code>
        </pre>
      </section>

      <section>
        <h2 id="dependencies">Dependencies</h2>
        <p>
          SPANCHOR automatically installs the following dependencies:
        </p>
        <ul>
          <li><code>numpy</code> - Numerical computing</li>
          <li><code>pandas</code> - Data analysis</li>
          <li><code>scikit-learn</code> - Machine learning utilities</li>
          <li><code>requests</code> - HTTP library</li>
          <li><code>pydantic</code> - Data validation</li>
        </ul>
      </section>

      <section>
        <h2 id="next-steps">Next Steps</h2>
        <p>
          Once installed, check out the <a href="/docs/quickstart" className="text-accent hover:underline">Quickstart guide</a> to run your first test.
        </p>
      </section>
    </DocumentationPage>
  );
};

export default Installation;
