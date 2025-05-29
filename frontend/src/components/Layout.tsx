import React, { useState } from 'react';
import { 
  BarChart3, 
  Settings, 
  TrendingUp, 
  Bell, 
  Menu,
  X,
  Home,
  DollarSign
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  currentPage?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
}

const navItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <Home size={20} />,
    href: '/'
  },
  {
    id: 'bloomberg',
    label: 'Bloomberg Live',
    icon: <DollarSign size={20} />,
    href: '/bloomberg'
  },
  {
    id: 'tickers',
    label: 'Tickers',
    icon: <TrendingUp size={20} />,
    href: '/tickers'
  },
  {
    id: 'charts',
    label: 'Charts',
    icon: <BarChart3 size={20} />,
    href: '/charts'
  },
  {
    id: 'settlement',
    label: 'Settlement',
    icon: <TrendingUp size={20} />,
    href: '/settlement'
  },
  {
    id: 'alerts',
    label: 'Alerts',
    icon: <Bell size={20} />,
    href: '/alerts'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings size={20} />,
    href: '/settings'
  }
];

export const Layout: React.FC<LayoutProps> = ({ children, currentPage = 'dashboard' }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`
        bg-white shadow-lg transition-all duration-300 ease-in-out
        ${sidebarCollapsed ? 'w-16' : 'w-64'}
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
        fixed lg:relative lg:translate-x-0 h-full z-30
      `}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <h1 className="text-xl font-bold text-gray-800">
                Metals Dashboard
              </h1>
            )}
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors hidden lg:block"
            >
              {sidebarCollapsed ? <Menu size={20} /> : <X size={20} />}
            </button>
            <button
              onClick={toggleMobileMenu}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors lg:hidden"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.id}>
                <a
                  href={item.href}
                  className={`
                    flex items-center p-3 rounded-lg transition-colors
                    ${currentPage === item.id 
                      ? 'bg-blue-100 text-blue-700 border-r-4 border-blue-700' 
                      : 'text-gray-600 hover:bg-gray-100'
                    }
                    ${sidebarCollapsed ? 'justify-center' : 'justify-start'}
                  `}
                  title={sidebarCollapsed ? item.label : undefined}
                >
                  <span className="flex-shrink-0">
                    {item.icon}
                  </span>
                  {!sidebarCollapsed && (
                    <span className="ml-3 font-medium">
                      {item.label}
                    </span>
                  )}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={toggleMobileMenu}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top Bar */}
        <header className="bg-white shadow-sm border-b border-gray-200 p-4 lg:hidden">
          <div className="flex items-center justify-between">
            <button
              onClick={toggleMobileMenu}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu size={20} />
            </button>
            <h1 className="text-lg font-semibold text-gray-800">
              Metals Dashboard
            </h1>
            <div className="w-10" /> {/* Spacer */}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}; 