import { Outlet } from 'react-router';
import { Toaster } from '@/app/components/ui/sonner';

export default function AuthRoot() {
  return (
    <>
      <Outlet />
      <Toaster richColors position="top-right" />
    </>
  );
}
