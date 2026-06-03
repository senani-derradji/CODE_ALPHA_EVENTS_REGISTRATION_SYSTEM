import { Link } from 'react-router';
import { motion } from 'motion/react';
import { MapPin, Calendar, Users, Clock } from 'lucide-react';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { Progress } from '@/app/components/ui/progress';
import { formatDate, getCapacityColor, truncate } from '@/utils';
import type { Event } from '@/types';

interface Props {
  event: Event;
  index?: number;
  onRegister?: (id: number) => void;
  isRegistering?: boolean;
  isRegistered?: boolean;
}

export default function EventCard({ event, index = 0, onRegister, isRegistering, isRegistered }: Props) {
  const capacityPct = Math.min(100, ((event.registered_count ?? 0) / event.max_attendees) * 100);
  const isFull = (event.registered_count ?? 0) >= event.max_attendees;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className="bg-card border border-border rounded-xl overflow-hidden hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 flex flex-col"
    >
      <div className="h-2 bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500" />
      <div className="p-5 flex flex-col flex-1">
        <div className="flex items-start justify-between gap-2 mb-3">
          <h3 className="font-semibold text-base leading-tight line-clamp-2 flex-1"
            style={{ fontFamily: 'var(--font-display)' }}>
            {event.title}
          </h3>
          {isFull ? (
            <Badge variant="destructive" className="shrink-0 text-xs">Full</Badge>
          ) : (
            <Badge variant="secondary" className="shrink-0 text-xs bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400">
              Open
            </Badge>
          )}
        </div>

        <p className="text-sm text-muted-foreground mb-4 flex-1 leading-relaxed">
          {truncate(event.description, 100)}
        </p>

        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="w-3.5 h-3.5 shrink-0 text-primary" />
            <span>{formatDate(event.start_time)}</span>
            <span>–</span>
            <span>{formatDate(event.end_time)}</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <MapPin className="w-3.5 h-3.5 shrink-0 text-primary" />
            <span className="truncate">{event.location}</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <Users className="w-3.5 h-3.5 shrink-0 text-primary" />
            <span className={getCapacityColor((event.registered_count ?? 0), event.max_attendees)}>
              {(event.registered_count ?? 0)} / {event.max_attendees}
            </span>
            <span className="text-muted-foreground">registered</span>
          </div>
        </div>

        <Progress value={capacityPct} className="h-1.5 mb-4" />

        <div className="flex items-center gap-2 mt-auto">
          <Button variant="outline" size="sm" asChild className="flex-1">
            <Link to={`/events/${event.id}`}>View Details</Link>
          </Button>
          {onRegister && (
            <Button
              size="sm"
              className="flex-1"
              disabled={isFull || isRegistered || isRegistering}
              onClick={() => onRegister(event.id)}
            >
              {isRegistered ? 'Registered' : isFull ? 'Full' : isRegistering ? 'Registering…' : 'Register'}
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
