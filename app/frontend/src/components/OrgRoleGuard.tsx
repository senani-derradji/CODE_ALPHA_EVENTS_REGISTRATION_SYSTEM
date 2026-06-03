import { Navigate, Outlet } from 'react-router';
import { useAuth } from '@/store/AuthContext';

export default function OrgRoleGuard() {
  const { user } = useAuth();
  if (!user || !['organization', 'admin'].includes(user.role)) {
    return <Navigate to="/dashboard/user" replace />;
  }
  return <Outlet />;
}
