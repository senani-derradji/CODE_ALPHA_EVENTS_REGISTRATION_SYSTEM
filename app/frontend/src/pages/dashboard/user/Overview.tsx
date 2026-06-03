import { motion } from 'motion/react';
import { Calendar, Ticket, CheckCircle, Clock } from 'lucide-react';
import { Link } from 'react-router';
import { useAuth } from '@/store/AuthContext';
import { useRegistrationsByUser } from '@/hooks/useRegistrations';
import { useEvents } from '@/hooks/useEvents';
import StatCard from '@/components/StatCard';
import PageHeader from '@/components/PageHeader';
import { Button } from '@/app/components/ui/button';
import { formatDate, getStatusColor } from '@/utils';

export default function UserOverview() {
  const { user } = useAuth();
  const { data: myRegs } = useRegistrationsByUser(user?.id ?? 0);
  const { data: events } = useEvents();

  const confirmed = myRegs?.filter((r) => r.status === 'confirmed').length ?? 0;
  const pending = myRegs?.filter((r) => r.status === 'pending').length ?? 0;
  const upcoming = events?.filter((e) => new Date(e.start_time) > new Date()).length ?? 0;

  const recentRegs = myRegs?.slice(0, 5) ?? [];

  return (
    <div>
      <PageHeader
        title={`Hello, ${user?.full_name?.split(' ')[0] ?? 'there'} 👋`}
        description="Here's what's happening with your events"
        action={<Button asChild><Link to="/events">Browse Events</Link></Button>}
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="My Registrations" value={myRegs?.length ?? 0} icon={Ticket} color="indigo" index={0} />
        <StatCard title="Confirmed" value={confirmed} icon={CheckCircle} color="emerald" index={1} />
        <StatCard title="Pending" value={pending} icon={Clock} color="amber" index={2} />
        <StatCard title="Upcoming Events" value={upcoming} icon={Calendar} color="violet" index={3} />
      </div>

      <div className="bg-card border border-border rounded-xl">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold" style={{ fontFamily: 'var(--font-display)' }}>Recent Registrations</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/dashboard/user/registrations">View all</Link>
          </Button>
        </div>
        <div className="divide-y divide-border">
          {recentRegs.length === 0 ? (
            <div className="px-5 py-8 text-center text-muted-foreground text-sm">
              No registrations yet. <Link to="/events" className="text-primary hover:underline">Browse events</Link>
            </div>
          ) : (
            recentRegs.map((reg, i) => {
              const event = events?.find((e) => e.id === reg.event_id);
              return (
                <motion.div
                  key={reg.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className="px-5 py-3.5 flex items-center justify-between gap-4"
                >
                  <div>
                    <p className="text-sm font-medium">{event?.title ?? `Event #${reg.event_id}`}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {event ? formatDate(event.start_time) : '—'}
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${getStatusColor(reg.status)}`}>
                    {reg.status}
                  </span>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
