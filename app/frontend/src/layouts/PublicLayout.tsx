import { Outlet } from 'react-router';
import { Toaster } from '@/app/components/ui/sonner';
import Navbar from '@/components/Navbar';

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Toaster richColors position="top-right" />
    </div>
  );
}
