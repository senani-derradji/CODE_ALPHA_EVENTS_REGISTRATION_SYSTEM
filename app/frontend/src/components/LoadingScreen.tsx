import { motion } from 'motion/react';
import { Calendar } from 'lucide-react';

export default function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center gap-4"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center"
        >
          <Calendar className="w-6 h-6 text-primary-foreground" />
        </motion.div>
        <p className="text-muted-foreground text-sm">Loading…</p>
      </motion.div>
    </div>
  );
}
