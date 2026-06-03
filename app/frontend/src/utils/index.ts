import { format, parseISO } from 'date-fns';
import type { UserRole, RegistrationStatus } from '@/types';

export function formatDate(dateStr: string) {
  try {
    return format(parseISO(dateStr), 'MMM d, yyyy');
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateStr: string) {
  try {
    return format(parseISO(dateStr), 'MMM d, yyyy · h:mm a');
  } catch {
    return dateStr;
  }
}

export function getRoleBadgeVariant(role: UserRole) {
  switch (role) {
    case 'admin': return 'destructive' as const;
    case 'organization': return 'default' as const;
    default: return 'secondary' as const;
  }
}

export function getRoleLabel(role: UserRole) {
  switch (role) {
    case 'admin': return 'Admin';
    case 'organization': return 'Organization';
    default: return 'User';
  }
}

export function getStatusColor(status: RegistrationStatus) {
  switch (status) {
    case 'confirmed': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-400';
    case 'pending': return 'text-amber-600 bg-amber-50 dark:bg-amber-950 dark:text-amber-400';
    case 'cancelled': return 'text-red-600 bg-red-50 dark:bg-red-950 dark:text-red-400';
  }
}

export function getCapacityColor(registered: number, capacity: number) {
  const pct = registered / capacity;
  if (pct >= 1) return 'text-red-500';
  if (pct >= 0.8) return 'text-amber-500';
  return 'text-emerald-500';
}

export function truncate(str: string, len = 120) {
  return str.length > len ? str.slice(0, len) + '…' : str;
}
