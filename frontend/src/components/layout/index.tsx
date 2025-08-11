import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  MessageSquare, 
  Database, 
  Code, 
  History, 
  BarChart3, 
  Menu,
  Sun,
  Moon,
  Settings,
  HelpCircle
} from 'lucide-react';
import { Button } from '../ui/button';
import { useTheme } from '../theme-provider';
import { cn } from '../../utils/cn';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { theme, setTheme } = useTheme();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'Schema Explorer', href: '/schema', icon: Database },
    { name: 'SQL Editor', href: '/sql', icon: Code },
    { name: 'Query History', href: '/history', icon: History },
  ];

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className={cn(
        "bg-card border-r border-border transition-all duration-300 ease-in-out",
        sidebarOpen ? "w-64" : "w-16"
      )}>
        {/* Header */}
        <div className="flex items-center justify-between p-4">
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-foreground">
              Warehouse Copilot
            </h1>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="h-8 w-8"
          >
            <Menu className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="mt-4">
          <div className="space-y-1 px-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                  title={sidebarOpen ? undefined : item.name}
                >
                  <Icon className={cn("h-5 w-5", sidebarOpen && "mr-3")} />
                  {sidebarOpen && (
                    <span className="truncate">{item.name}</span>
                  )}
                </NavLink>
              );
            })}
          </div>
        </nav>

        {/* Bottom section */}
        <div className="absolute bottom-4 left-0 right-0 px-2">
          <div className="space-y-1">
            <Button
              variant="ghost"
              size={sidebarOpen ? "default" : "icon"}
              onClick={toggleTheme}
              className="w-full justify-start"
              title={sidebarOpen ? undefined : "Toggle theme"}
            >
              {theme === 'dark' ? (
                <Sun className={cn("h-5 w-5", sidebarOpen && "mr-3")} />
              ) : (
                <Moon className={cn("h-5 w-5", sidebarOpen && "mr-3")} />
              )}
              {sidebarOpen && (
                <span>Toggle theme</span>
              )}
            </Button>
            
            <Button
              variant="ghost"
              size={sidebarOpen ? "default" : "icon"}
              className="w-full justify-start"
              title={sidebarOpen ? undefined : "Settings"}
            >
              <Settings className={cn("h-5 w-5", sidebarOpen && "mr-3")} />
              {sidebarOpen && <span>Settings</span>}
            </Button>
            
            <Button
              variant="ghost"
              size={sidebarOpen ? "default" : "icon"}
              className="w-full justify-start"
              title={sidebarOpen ? undefined : "Help"}
            >
              <HelpCircle className={cn("h-5 w-5", sidebarOpen && "mr-3")} />
              {sidebarOpen && <span>Help</span>}
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-hidden">
        <main className="h-full overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;