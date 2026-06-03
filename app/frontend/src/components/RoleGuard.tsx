import { Navigate, Outlet } from 'react-router';
import { useAuth } from '@/store/AuthContext';
import type { UserRole } from '@/types';

interface Props {
  roles: UserRole[];
  redirectTo?: string;
}

export default function RoleGuard({ roles, redirectTo = '/dashboard/user' }: Props) {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    return <Navigate to={redirectTo} replace />;
  }

  return <Outlet />;
}
