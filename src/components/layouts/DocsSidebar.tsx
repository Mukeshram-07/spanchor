import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronDown, Menu } from 'lucide-react';
import Drawer from '../ui/Drawer';
import { cn } from '../../utils/cn';

interface NavItem {
  label: string;
  href: string;
}

interface NavSection {
  label: string;
  items: NavItem[];
}

interface DocsSidebarProps {
  currentPath?: string;
  onNavigate?: () => void;
}

const navigation: NavSection[] = [
  {
    label: 'Introduction',
    items: [{ label: 'Overview', href: '/docs' }],
  },
  {
    label: 'Getting Started',
    items: [
      { label: 'Installation', href: '/docs/installation' },
      { label: 'Quickstart', href: '/docs/quickstart' },
    ],
  },
  {
    label: 'Core Concepts',
    items: [
      { label: 'Concepts', href: '/docs/concepts' },
      { label: 'Anchors', href: '/docs/anchors' },
      { label: 'Gold Sets', href: '/docs/gold-sets' },
    ],
  },
  {
    label: 'Evaluation',
    items: [
      { label: 'Metrics', href: '/docs/metrics' },
      { label: 'Comparison', href: '/docs/comparison' },
    ],
  },
  {
    label: 'Advanced',
    items: [
      { label: 'Adapters', href: '/docs/adapters' },
      { label: 'CLI', href: '/docs/cli' },
    ],
  },
  {
    label: 'Examples',
    items: [{ label: 'Testing Examples', href: '/docs/testing' }],
  },
  {
    label: 'Reference',
    items: [{ label: 'Limitations', href: '/docs/limitations' }],
  },
];

// Helper defined at module scope — safe to use anywhere
function getActiveSection(pathname: string): Set<string> {
  return new Set(
    navigation
      .filter((s) => s.items.some((i) => i.href === pathname || pathname.startsWith(i.href + '/')))
      .map((s) => s.label)
  );
}

interface SidebarSectionProps {
  section: NavSection;
  isExpanded: boolean;
  onToggle: () => void;
  isActive: (href: string) => boolean;
  onItemClick?: () => void;
}

const SidebarSection: React.FC<SidebarSectionProps> = ({
  section,
  isExpanded,
  onToggle,
  isActive,
  onItemClick,
}) => {
  const hasActiveItem = section.items.some((item) => isActive(item.href));

  return (
    <div className="mb-1">
      <button
        onClick={onToggle}
        className={cn(
          'w-full flex items-center justify-between px-3 py-2 rounded font-medium transition-colors text-sm',
          hasActiveItem
            ? 'bg-sky-50 text-sky-700'
            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
        )}
      >
        <span>{section.label}</span>
        <ChevronDown
          className={cn(
            'w-4 h-4 transition-transform text-slate-400',
            isExpanded ? 'rotate-180' : ''
          )}
        />
      </button>

      {isExpanded && (
        <div className="mt-1 ml-2 border-l border-slate-200 pl-3 py-1">
          {section.items.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              onClick={onItemClick}
              className={cn(
                'block px-3 py-1.5 rounded text-sm transition-colors',
                isActive(item.href)
                  ? 'bg-sky-50 text-sky-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  pathname: string;
}

const MobileNavDrawer: React.FC<MobileDrawerProps> = ({ isOpen, onClose, pathname }) => {
  const isActive = (href: string) => pathname === href;

  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    () => getActiveSection(pathname)
  );

  const toggleSection = (label: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(label)) {
        next.delete(label);
      } else {
        next.add(label);
      }
      return next;
    });
  };

  return (
    <Drawer isOpen={isOpen} onClose={onClose} side="left" title="Documentation">
      <nav className="space-y-1">
        {navigation.map((section) => (
          <SidebarSection
            key={section.label}
            section={section}
            isExpanded={expandedSections.has(section.label)}
            onToggle={() => toggleSection(section.label)}
            isActive={isActive}
            onItemClick={onClose}
          />
        ))}
      </nav>
    </Drawer>
  );
};

const DocsSidebar: React.FC<DocsSidebarProps> = ({ onNavigate }) => {
  const location = useLocation();

  // isActive defined BEFORE any useState that references it
  const isActive = (href: string) => location.pathname === href;

  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    () => getActiveSection(location.pathname)
  );
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  const toggleSection = (label: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(label)) {
        next.delete(label);
      } else {
        next.add(label);
      }
      return next;
    });
  };

  const handleItemClick = () => {
    onNavigate?.();
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileDrawerOpen(true)}
        className="md:hidden fixed bottom-4 right-4 z-40 p-3 bg-sky-600 text-white rounded-lg shadow-lg hover:bg-sky-700 transition-colors"
        aria-label="Open documentation navigation"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Desktop Sidebar */}
      <aside className="hidden md:block w-60 flex-shrink-0 bg-white border-r border-slate-200 overflow-y-auto">
        <nav className="p-4 space-y-1" aria-label="Documentation navigation">
          {navigation.map((section) => (
            <SidebarSection
              key={section.label}
              section={section}
              isExpanded={expandedSections.has(section.label)}
              onToggle={() => toggleSection(section.label)}
              isActive={isActive}
              onItemClick={handleItemClick}
            />
          ))}
        </nav>
      </aside>

      {/* Mobile Drawer */}
      <MobileNavDrawer
        isOpen={isMobileDrawerOpen}
        onClose={() => setIsMobileDrawerOpen(false)}
        pathname={location.pathname}
      />
    </>
  );
};

export default DocsSidebar;
