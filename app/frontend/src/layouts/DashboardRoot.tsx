import { Outlet } from 'react-router';
import { Toaster } from '@/app/components/ui/sonner';

export default function DashboardRoot() {
  return (
    <>
      <Outlet />
      <Toaster richColors position="top-right" />
    </>
  );
}
