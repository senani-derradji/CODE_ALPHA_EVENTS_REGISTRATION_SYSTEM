import { Link } from 'react-router';
import { motion } from 'motion/react';
import { ArrowRight, Calendar, Users, Zap, Shield, TrendingUp, Star } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { useEvents } from '@/hooks/useEvents';
import EventCard from '@/components/EventCard';

export default function Home() {
  const { data: events } = useEvents();
  const featuredEvents = events?.slice(0, 3) ?? [];

  return (
    <div className="overflow-hidden">
      {/* Hero */}
      <section className="relative bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
        <div className="absolute inset-0">
          {Array.from({ length: 30 }).map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-white/20 rounded-full"
              style={{
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
              }}
            />
          ))}
        </div>
        <div className="relative max-w-7xl mx-auto px-4 py-28 md:py-36 text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 rounded-full px-4 py-1.5 text-sm text-indigo-200 mb-6 backdrop-blur-sm">
              <Star className="w-3.5 h-3.5" />
              Trusted by 48,000+ event managers worldwide
            </div>
            <h1 className="mb-6 text-white" style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(2.5rem, 5vw, 4rem)', fontWeight: 800, lineHeight: 1.1 }}>
              Manage Events with<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-violet-300">
                Effortless Precision
              </span>
            </h1>
            <p className="text-indigo-200 text-xl max-w-2xl mx-auto mb-8 leading-relaxed">
              Create, manage, and grow your events. From small workshops to large conferences — EventHub handles everything.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Button size="lg" asChild className="bg-white text-indigo-900 hover:bg-indigo-50 font-semibold">
                <Link to="/auth/register">
                  Get started free <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="border-white/30 text-white hover:bg-white/10">
                <Link to="/events">Browse Events</Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: '12,400+', label: 'Events Created' },
            { value: '48,000+', label: 'Happy Users' },
            { value: '85+', label: 'Countries' },
            { value: '99.9%', label: 'Uptime SLA' },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <p className="font-bold text-2xl md:text-3xl text-primary" style={{ fontFamily: 'var(--font-display)' }}>
                {stat.value}
              </p>
              <p className="text-muted-foreground text-sm mt-1">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-3"
            style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700 }}
          >
            Everything you need
          </motion.h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            A complete platform with all the tools to create exceptional events.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { icon: Calendar, title: 'Event Management', description: 'Create and manage events with rich details, capacity controls, and scheduling.', color: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400' },
            { icon: Users, title: 'Registration System', description: 'Streamlined registration with status tracking and cancellation management.', color: 'bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400' },
            { icon: TrendingUp, title: 'Analytics Dashboard', description: 'Real-time insights with charts and metrics to optimize event performance.', color: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400' },
            { icon: Shield, title: 'Role-Based Access', description: 'Granular permissions for users, organizations, and administrators.', color: 'bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400' },
            { icon: Zap, title: 'Instant Notifications', description: 'Real-time toast notifications keep your team updated on every action.', color: 'bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400' },
            { icon: Star, title: 'OAuth Integration', description: 'Sign in with Google or Microsoft for a seamless authentication experience.', color: 'bg-cyan-50 text-cyan-600 dark:bg-cyan-950 dark:text-cyan-400' },
          ].map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-shadow"
            >
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 ${f.color}`}>
                <f.icon className="w-5 h-5" />
              </div>
              <h3 className="font-semibold mb-2" style={{ fontFamily: 'var(--font-display)' }}>{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Featured Events */}
      {featuredEvents.length > 0 && (
        <section className="bg-muted/30 py-20">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="font-bold" style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem' }}>
                  Upcoming Events
                </h2>
                <p className="text-muted-foreground mt-1">Don't miss these exciting upcoming events</p>
              </div>
              <Button variant="outline" asChild>
                <Link to="/events">View all <ArrowRight className="w-4 h-4 ml-2" /></Link>
              </Button>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredEvents.map((event, i) => (
                <EventCard key={event.id} event={event} index={i} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-10 md:p-16 text-center text-white"
        >
          <h2 className="mb-4" style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700 }}>
            Ready to host your next event?
          </h2>
          <p className="text-indigo-100 mb-8 max-w-xl mx-auto">
            Join thousands of organizers who trust EventHub to run seamless events.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button size="lg" className="bg-white text-indigo-900 hover:bg-indigo-50 font-semibold" asChild>
              <Link to="/auth/register">Start for free</Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10" asChild>
              <Link to="/auth/login">Sign in</Link>
            </Button>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
