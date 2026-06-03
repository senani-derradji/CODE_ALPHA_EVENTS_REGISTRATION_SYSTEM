import { Link, useLocation } from 'react-router';
import { motion, AnimatePresence } from 'motion/react';
import {
  LayoutDashboard, Calendar, Users, Building, BarChart3, Settings,
  X, CalendarPlus, ClipboardList, PieChart, UserCircle, Star, FileText,
} from 'lucide-react';
import { useAuth } from '@/store/AuthContext';
import { cn } from '@/app/components/ui/utils';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
}

const userNav: NavItem[] = [
  { label: 'Overview', path: '/dashboard/user', icon: LayoutDashboard },
  { label: 'My Registrations', path: '/dashboard/user/registrations', icon: ClipboardList },
  { label: 'Browse Events', path: '/events', icon: Calendar },
  { label: 'Profile', path: '/dashboard/user/profile', icon: UserCircle },
];

const orgNav: NavItem[] = [
  { label: 'Overview', path: '/dashboard/org', icon: LayoutDashboard },
  { label: 'My Events', path: '/dashboard/org/events', icon: Calendar },
  { label: 'Create Event', path: '/dashboard/org/events/new', icon: CalendarPlus },
  { label: 'Analytics', path: '/dashboard/org/analytics', icon: PieChart },
  { label: 'Profile', path: '/dashboard/user/profile', icon: UserCircle },
];

const adminNav: NavItem[] = [
  { label: 'Overview', path: '/dashboard/admin', icon: LayoutDashboard },
  { label: 'Users', path: '/dashboard/admin/users', icon: Users },
  { label: 'Organizations', path: '/dashboard/admin/organizations', icon: Building },
  { label: 'Events', path: '/dashboard/admin/events', icon: Calendar },
  { label: 'Registrations', path: '/dashboard/admin/registrations', icon: ClipboardList },
  { label: 'Statistics', path: '/dashboard/admin/statistics', icon: BarChart3 },
];

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: Props) {
  const { user } = useAuth();
  const location = useLocation();

  const navItems =
    user?.role === 'admin' ? adminNav
    : user?.role === 'organization' ? orgNav
    : userNav;

  const roleLabel = user?.role === 'admin' ? 'Admin' : user?.role === 'organization' ? 'Organization' : 'User';
  const roleColor = user?.role === 'admin' ? 'bg-rose-100 text-rose-700 dark:bg-rose-900 dark:text-rose-300'
    : user?.role === 'organization' ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
    : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      <div className="h-16 flex items-center px-4 border-b border-sidebar-border">
        <Link to="/" className="flex items-center gap-2 flex-1">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Calendar className="w-4 h-4 text-primary-foreground" />
          </div>
          <span className="font-bold text-base" style={{ fontFamily: 'var(--font-display)' }}>
            EventHub
          </span>
        </Link>
        <Button variant="ghost" size="icon" className="lg:hidden" onClick={onClose}>
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="px-3 py-3 border-b border-sidebar-border">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-semibold">
            {user?.full_name?.slice(0, 2).toUpperCase() ?? 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name ?? user?.username}</p>
            <span className={cn('text-xs px-1.5 py-0.5 rounded-md font-medium', roleColor)}>
              {roleLabel}
            </span>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground'
              )}
            >
              <Icon className={cn('w-4 h-4 shrink-0', isActive ? 'text-sidebar-primary' : 'opacity-60')} />
              <span className="flex-1">{item.label}</span>
              {item.badge && (
                <Badge variant="secondary" className="text-xs">{item.badge}</Badge>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-sidebar-border">
        <p className="text-xs text-muted-foreground px-3">EventHub v1.0 © 2024</p>
      </div>
    </div>
  );

  return (
    <>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {open && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed left-0 top-0 bottom-0 z-50 w-64 bg-sidebar text-sidebar-foreground border-r border-sidebar-border lg:hidden"
          >
            <SidebarContent />
          </motion.aside>
        )}
      </AnimatePresence>

      <aside className="hidden lg:flex w-64 shrink-0 flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border h-screen">
        <SidebarContent />
      </aside>
    </>
  );
}
