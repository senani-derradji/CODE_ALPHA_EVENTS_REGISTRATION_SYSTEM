import { useParams, Link } from 'react-router';
import { motion } from 'motion/react';
import { Calendar, MapPin, Users, ArrowLeft, Clock, Ticket } from 'lucide-react';
import { useEvent } from '@/hooks/useEvents';
import { useRegistrationsByUser, useRegisterForEvent, useCancelRegistration } from '@/hooks/useRegistrations';
import { useAuth } from '@/store/AuthContext';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Progress } from '@/app/components/ui/progress';
import { Skeleton } from '@/app/components/ui/skeleton';
import { formatDate, formatDateTime, getCapacityColor } from '@/utils';

export default function EventDetails() {
  const { id } = useParams<{ id: string }>();
  const eventId = Number(id);
  const { data: event, isLoading } = useEvent(eventId);
  const { user } = useAuth();
  const { data: myRegs } = useRegistrationsByUser(user?.id ?? 0);
  const { mutate: register, isPending: registering } = useRegisterForEvent();
  const { mutate: cancel, isPending: cancelling } = useCancelRegistration();

  const myReg = myRegs?.find((r) => r.event_id === eventId);
  const isFull = event ? (event.registered_count ?? 0) >= event.max_attendees : false;
  const capacityPct = event ? Math.min(100, ((event.registered_count ?? 0) / event.max_attendees) * 100) : 0;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (!event) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 text-center">
        <p className="text-muted-foreground">Event not found.</p>
        <Button asChild className="mt-4"><Link to="/events">Back to Events</Link></Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <Button variant="ghost" asChild className="mb-6 -ml-2">
        <Link to="/events"><ArrowLeft className="w-4 h-4 mr-2" /> Back to Events</Link>
      </Button>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-8 text-white mb-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="mb-2" style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, lineHeight: 1.2 }}>
                {event.title}
              </h1>
              {isFull ? (
                <Badge className="bg-white/20 text-white border-white/30">Fully Booked</Badge>
              ) : (
                <Badge className="bg-white/20 text-white border-white/30">Registration Open</Badge>
              )}
            </div>
            <div className="text-right shrink-0">
              <p className="text-3xl font-bold">{(event.registered_count ?? 0)}</p>
              <p className="text-indigo-200 text-sm">/ {event.max_attendees} spots</p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <div className="bg-card border border-border rounded-xl p-6">
              <h2 className="font-semibold mb-3" style={{ fontFamily: 'var(--font-display)' }}>About this event</h2>
              <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">{event.description}</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <h2 className="font-semibold mb-4" style={{ fontFamily: 'var(--font-display)' }}>Event Details</h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center shrink-0">
                    <Calendar className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Start Date</p>
                    <p className="text-sm text-muted-foreground">{formatDateTime(event.start_time)}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-violet-50 dark:bg-violet-950 flex items-center justify-center shrink-0">
                    <Clock className="w-4 h-4 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">End Date</p>
                    <p className="text-sm text-muted-foreground">{formatDateTime(event.end_time)}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center shrink-0">
                    <MapPin className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">{event.location}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <Users className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-sm">Capacity</h3>
              </div>
              <p className={`text-2xl font-bold mb-1 ${getCapacityColor((event.registered_count ?? 0), event.max_attendees)}`}>
                {(event.registered_count ?? 0)} / {event.max_attendees}
              </p>
              <Progress value={capacityPct} className="h-2 mb-2" />
              <p className="text-xs text-muted-foreground">{event.max_attendees - (event.registered_count ?? 0)} spots remaining</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Ticket className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-sm">Registration</h3>
              </div>
              {!user ? (
                <div className="text-center">
                  <p className="text-sm text-muted-foreground mb-3">Sign in to register</p>
                  <Button asChild className="w-full"><Link to="/auth/login">Sign in</Link></Button>
                </div>
              ) : myReg ? (
                <div>
                  <div className="bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 rounded-lg p-3 text-sm text-center mb-3">
                    You are registered for this event!
                  </div>
                  <Button
                    variant="destructive"
                    className="w-full"
                    disabled={cancelling}
                    onClick={() => cancel(myReg.id)}
                  >
                    {cancelling ? 'Cancelling…' : 'Cancel Registration'}
                  </Button>
                </div>
              ) : (
                <Button
                  className="w-full"
                  disabled={isFull || registering}
                  onClick={() => register(event.id)}
                >
                  {isFull ? 'Event Full' : registering ? 'Registering…' : 'Register Now'}
                </Button>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
