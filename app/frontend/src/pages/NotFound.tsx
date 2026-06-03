import { Link } from 'react-router';
import { motion } from 'motion/react';
import { Button } from '@/app/components/ui/button';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center px-4"
      >
        <p className="text-8xl font-black text-primary/20 mb-4" style={{ fontFamily: 'var(--font-display)' }}>404</p>
        <h1 className="font-bold mb-2" style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem' }}>Page not found</h1>
        <p className="text-muted-foreground mb-6">The page you're looking for doesn't exist.</p>
        <Button asChild>
          <Link to="/"><Home className="w-4 h-4 mr-2" /> Back to Home</Link>
        </Button>
      </motion.div>
    </div>
  );
}
