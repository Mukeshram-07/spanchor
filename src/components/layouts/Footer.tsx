import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const links = [
    { label: 'Documentation', href: '/docs' },
    { label: 'GitHub', href: 'https://github.com/Mukeshram-07/spanchor', external: true },
    { label: 'PyPI', href: 'https://pypi.org/project/spanchor/', external: true },
    { label: 'Examples', href: '/examples' },
    { label: 'API', href: '/api' },
  ];

  return (
    <footer
      className="bg-secondary-bg border-t border-border mt-24"
      role="contentinfo"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Top Section: Branding & Description */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* Branding */}
          <div>
            <h2 className="text-lg font-bold text-text-primary mb-2">SPANCHOR</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              Source-anchored regression testing for RAG retrieval pipelines.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-sm font-semibold text-text-primary mb-4">Resources</h3>
            <nav className="flex flex-col gap-2" aria-label="Footer resources">
              {links.map((link) => (
                <React.Fragment key={link.href}>
                  {link.external ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-text-secondary hover:text-accent transition-colors"
                      aria-label={`${link.label} (opens in new tab)`}
                    >
                      {link.label}
                    </a>
                  ) : (
                    <Link
                      to={link.href}
                      className="text-sm text-text-secondary hover:text-accent transition-colors"
                    >
                      {link.label}
                    </Link>
                  )}
                </React.Fragment>
              ))}
            </nav>
          </div>

          {/* Metadata */}
          <div>
            <h3 className="text-sm font-semibold text-text-primary mb-4">Info</h3>
            <ul className="flex flex-col gap-2 text-sm text-text-secondary">
              <li>
                <span className="font-medium">License:</span> Apache-2.0
              </li>
              <li>
                <span className="font-medium">Python:</span> 3.11 – 3.13
              </li>
              <li>
                <span className="font-medium">Type:</span> Package
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section: Copyright */}
        <div className="border-t border-border pt-8">
          <p className="text-center text-sm text-text-muted">
            © {currentYear} SPANCHOR. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
