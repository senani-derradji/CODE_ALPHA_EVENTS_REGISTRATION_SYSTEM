import { useState } from 'react';
import { Link } from 'react-router';
import { motion } from 'motion/react';
import { Ticket, Calendar, MapPin, ExternalLink, X } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';
import { useRegistrationsByUser, useCancelRegistration } from '@/hooks/useRegistrations';
import { useEvents } from '@/hooks/useEvents';
import PageHeader from '@/components/PageHeader';
import SearchBar from '@/components/SearchBar';
import EmptyState from '@/components/EmptyState';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';
import { formatDate, getStatusColor } from '@/utils';

export default function MyRegistrations() {
  const { user } = useAuth();
  const { data: regs, isLoading } = useRegistrationsByUser(user?.id ?? 0);
  const { data: events } = useEvents();
  const { mutate: cancel, isPending } = useCancelRegistration();
  const [search, setSearch] = useState('');

  const filtered = (regs ?? []).filter((r) => {
    const event = events?.find((e) => e.id === r.event_id);
    return !search || event?.title.toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div>
      <PageHeader title="My Registrations" description="Track all your event registrations" />

      <div className="mb-4">
        <SearchBar value={search} onChange={setSearch} placeholder="Search by event name…" />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Ticket}
          title="No registrations"
          description="You haven't registered for any events yet."
          action={<Button asChild><Link to="/events">Browse Events</Link></Button>}
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((reg, i) => {
            const event = events?.find((e) => e.id === reg.event_id);
            return (
              <motion.div
                key={reg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="bg-card border border-border rounded-xl p-4 flex items-center gap-4"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <Ticket className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{event?.title ?? `Event #${reg.event_id}`}</p>
                  <div className="flex items-center gap-3 mt-1">
                    {event && (
                      <>
                        <span className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Calendar className="w-3 h-3" /> {formatDate(event.start_time)}
                        </span>
                        <span className="flex items-center gap-1 text-xs text-muted-foreground">
                          <MapPin className="w-3 h-3" /> {event.location}
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize shrink-0 ${getStatusColor(reg.status)}`}>
                  {reg.status}
                </span>
                <div className="flex items-center gap-1 shrink-0">
                  {event && (
                    <Button variant="ghost" size="icon" asChild className="h-8 w-8">
                      <Link to={`/events/${event.id}`}><ExternalLink className="w-3.5 h-3.5" /></Link>
                    </Button>
                  )}
                  {reg.status !== 'cancelled' && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive hover:text-destructive"
                      disabled={isPending}
                      onClick={() => cancel(reg.id)}
                    >
                      <X className="w-3.5 h-3.5" />
                    </Button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
