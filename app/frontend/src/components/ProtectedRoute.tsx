import { Navigate, Outlet, useLocation } from 'react-router';
import { useAuth } from '@/store/AuthContext';
import LoadingScreen from './LoadingScreen';

export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/auth/login" state={{ from: location }} replace />;

  return <Outlet />;
}
