import { Navigate, Outlet } from 'react-router';
import { useAuth } from '@/store/AuthContext';

export default function AdminRoleGuard() {
  const { user } = useAuth();
  if (!user || user.role !== 'admin') {
    return <Navigate to="/dashboard/user" replace />;
  }
  return <Outlet />;
}
