import { useState } from 'react';
import { Link } from 'react-router';
import { Plus, Edit, Trash2, Users, Calendar } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';
import { useEventsByOrganizer, useDeleteEvent } from '@/hooks/useEvents';
import PageHeader from '@/components/PageHeader';
import SearchBar from '@/components/SearchBar';
import EmptyState from '@/components/EmptyState';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Progress } from '@/app/components/ui/progress';
import { Skeleton } from '@/app/components/ui/skeleton';
import { formatDate } from '@/utils';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel,
  AlertDialogContent, AlertDialogDescription, AlertDialogFooter,
  AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '@/app/components/ui/alert-dialog';

export default function MyEvents() {
  const { user } = useAuth();
  const { data: events, isLoading } = useEventsByOrganizer(user?.id ?? 0);
  const { mutate: deleteEvent } = useDeleteEvent();
  const [search, setSearch] = useState('');

  const filtered = (events ?? []).filter((e) =>
    !search || e.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <PageHeader
        title="My Events"
        description="Manage all your events"
        action={
          <Button asChild>
            <Link to="/dashboard/org/events/new"><Plus className="w-4 h-4 mr-2" /> New Event</Link>
          </Button>
        }
      />

      <div className="mb-4">
        <SearchBar value={search} onChange={setSearch} placeholder="Search events…" />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-xl" />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No events"
          description="Create your first event to get started."
          action={<Button asChild><Link to="/dashboard/org/events/new">Create Event</Link></Button>}
        />
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <div className="divide-y divide-border">
            {filtered.map((event) => {
              const pct = Math.min(100, ((event.registered_count ?? 0) / event.max_attendees) * 100);
              const isActive = new Date(event.end_time) > new Date();
              return (
                <div key={event.id} className="p-4 flex items-center gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-sm truncate">{event.title}</p>
                      <Badge variant={isActive ? 'default' : 'secondary'} className="text-xs shrink-0">
                        {isActive ? 'Active' : 'Ended'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                      <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{formatDate(event.start_time)}</span>
                      <span className="flex items-center gap-1"><Users className="w-3 h-3" />{(event.registered_count ?? 0)}/{event.max_attendees}</span>
                    </div>
                    <Progress value={pct} className="h-1.5 w-48" />
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/dashboard/org/events/${event.id}/registrations`}>
                        <Users className="w-3.5 h-3.5 mr-1" /> Registrations
                      </Link>
                    </Button>
                    <Button variant="outline" size="icon" className="h-8 w-8" asChild>
                      <Link to={`/dashboard/org/events/${event.id}/edit`}><Edit className="w-3.5 h-3.5" /></Link>
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="outline" size="icon" className="h-8 w-8 text-destructive hover:text-destructive">
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete event?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This will permanently delete "{event.title}" and all its registrations.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => deleteEvent(event.id)} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
