import { Outlet, Link } from 'react-router';
import { motion } from 'motion/react';
import { Calendar } from 'lucide-react';

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex bg-background">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 flex-col justify-between p-12 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full border border-white/20"
              style={{
                width: `${(i + 1) * 150}px`,
                height: `${(i + 1) * 150}px`,
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
              }}
            />
          ))}
        </div>
        <Link to="/" className="flex items-center gap-2 text-white z-10 relative">
          <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center">
            <Calendar className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold" style={{ fontFamily: 'var(--font-display)' }}>
            EventHub
          </span>
        </Link>
        <div className="z-10 relative">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-white mb-4" style={{ fontSize: '2.25rem', lineHeight: '1.2' }}>
              Manage events with<br />
              <span className="text-indigo-200">confidence</span>
            </h1>
            <p className="text-indigo-200 text-lg leading-relaxed">
              Create, manage, and grow your events with powerful tools built for modern teams.
            </p>
          </motion.div>
          <div className="mt-8 grid grid-cols-2 gap-4">
            {[
              { label: 'Events Created', value: '12,400+' },
              { label: 'Happy Users', value: '48,000+' },
              { label: 'Countries', value: '85+' },
              { label: 'Uptime', value: '99.9%' },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
                <p className="text-white font-bold text-xl">{stat.value}</p>
                <p className="text-indigo-200 text-sm">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
        <p className="text-indigo-300 text-sm z-10 relative">© 2024 EventHub. All rights reserved.</p>
      </div>
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center">
              <Calendar className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold" style={{ fontFamily: 'var(--font-display)' }}>
              EventHub
            </span>
          </div>
          <Outlet />
        </div>
      </div>
    </div>
  );
}
