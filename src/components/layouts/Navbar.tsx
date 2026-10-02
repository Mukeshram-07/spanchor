import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, GitBranch, Package, Command } from 'lucide-react';
import { SPANCHOR_VERSION_TAG } from '../../config/version';

const Navbar: React.FC = () => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { label: 'Docs', href: '/docs' },
    { label: 'Examples', href: '/examples' },
    { label: 'API', href: '/api' },
    { label: 'Architecture', href: '/architecture' },
  ];

  const isActive = (href: string) => {
    return location.pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Wordmark & Logo */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8">
                <img 
                  src="https://i.ibb.co/rK2bWRpk/Chat-GPT-Image-Sep-30-2026-11-35-30-PM.png" 
                  alt="SPANCHOR" 
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg text-slate-900 tracking-tight">SPANCHOR</span>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                  {SPANCHOR_VERSION_TAG}
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map(({ label, href }) => {
                const active = isActive(href);
                return (
                  <Link
                    key={href}
                    to={href}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                      active
                        ? 'text-sky-700 bg-sky-50 font-semibold'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    {label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Action Cluster */}
          <div className="hidden md:flex items-center gap-3">
            {/* Quick Command Keyhint */}
            <div className="hidden lg:flex items-center gap-1 px-2.5 py-1 bg-slate-100 text-slate-500 rounded border border-slate-200 text-xs font-mono">
              <Command className="w-3 h-3" />
              <span>K</span>
            </div>

            {/* PyPI Package Badge Link */}
            <a
              href="https://pypi.org/project/spanchor/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md border border-slate-200 transition-colors"
            >
              <Package className="w-3.5 h-3.5 text-sky-600" />
              <span>pip install spanchor</span>
            </a>

            {/* GitHub Repo Link */}
            <a
              href="https://github.com/Mukeshram-07/spanchor"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-md shadow-sm transition-colors"
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>GitHub</span>
            </a>
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setIsMobileOpen(!isMobileOpen)}
              className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
              aria-label="Toggle menu"
            >
              {isMobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {isMobileOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-6 space-y-3">
          <nav className="flex flex-col space-y-1">
            {navLinks.map(({ label, href }) => (
              <Link
                key={href}
                to={href}
                onClick={() => setIsMobileOpen(false)}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive(href)
                    ? 'bg-sky-50 text-sky-700 font-semibold'
                    : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                {label}
              </Link>
            ))}
          </nav>

          <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
            <a
              href="https://pypi.org/project/spanchor/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-2 text-xs font-mono text-slate-700 bg-slate-100 rounded-md"
            >
              <Package className="w-4 h-4 text-sky-600" />
              <span>pip install spanchor</span>
            </a>
            <a
              href="https://github.com/Mukeshram-07/spanchor"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-white bg-slate-900 rounded-md"
            >
              <GitBranch className="w-4 h-4" />
              <span>GitHub Repository</span>
            </a>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
