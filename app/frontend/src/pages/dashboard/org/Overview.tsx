import { motion } from 'motion/react';
import { Calendar, Users, BarChart3, TrendingUp, Plus } from 'lucide-react';
import { Link } from 'react-router';
import { useAuth } from '@/store/AuthContext';
import { useEventsByOrganizer } from '@/hooks/useEvents';
import { useRegistrationsByEvent } from '@/hooks/useRegistrations';
import StatCard from '@/components/StatCard';
import PageHeader from '@/components/PageHeader';
import { Button } from '@/app/components/ui/button';
import { formatDate } from '@/utils';

export default function OrgOverview() {
  const { user } = useAuth();
  const { data: events } = useEventsByOrganizer(user?.id ?? 0);

  const totalCapacity = events?.reduce((sum, e) => sum + e.max_attendees, 0) ?? 0;
  const totalRegistered = events?.reduce((sum, e) => sum + (e.registered_count ?? 0), 0) ?? 0;
  const activeEvents = events?.filter((e) => new Date(e.end_time) > new Date()).length ?? 0;
  const fillRate = totalCapacity > 0 ? Math.round((totalRegistered / totalCapacity) * 100) : 0;

  return (
    <div>
      <PageHeader
        title="Organization Dashboard"
        description="Manage your events and track registrations"
        action={
          <Button asChild>
            <Link to="/dashboard/org/events/new"><Plus className="w-4 h-4 mr-2" /> Create Event</Link>
          </Button>
        }
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Events" value={events?.length ?? 0} icon={Calendar} color="indigo" index={0} />
        <StatCard title="Active Events" value={activeEvents} icon={TrendingUp} color="emerald" index={1} />
        <StatCard title="Total Registrations" value={totalRegistered} icon={Users} color="violet" index={2} />
        <StatCard title="Fill Rate" value={`${fillRate}%`} icon={BarChart3} color="amber" index={3} />
      </div>

      <div className="bg-card border border-border rounded-xl">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold" style={{ fontFamily: 'var(--font-display)' }}>Your Events</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/dashboard/org/events">View all</Link>
          </Button>
        </div>
        <div className="divide-y divide-border">
          {!events?.length ? (
            <div className="px-5 py-8 text-center text-muted-foreground text-sm">
              No events yet. <Link to="/dashboard/org/events/new" className="text-primary hover:underline">Create your first event</Link>
            </div>
          ) : (
            events.slice(0, 5).map((event, i) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.04 }}
                className="px-5 py-3.5 flex items-center justify-between gap-4"
              >
                <div>
                  <p className="text-sm font-medium">{event.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{formatDate(event.start_time)} · {event.location}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-muted-foreground">
                    {(event.registered_count ?? 0)}/{event.max_attendees}
                  </span>
                  <Button variant="outline" size="sm" asChild>
                    <Link to={`/dashboard/org/events/${event.id}/edit`}>Edit</Link>
                  </Button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
