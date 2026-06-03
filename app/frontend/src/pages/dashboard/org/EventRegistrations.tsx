import { useParams } from 'react-router';
import { Users } from 'lucide-react';
import { useEvent } from '@/hooks/useEvents';
import { useRegistrationsByEvent } from '@/hooks/useRegistrations';
import PageHeader from '@/components/PageHeader';
import EmptyState from '@/components/EmptyState';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Avatar, AvatarFallback } from '@/app/components/ui/avatar';
import { Progress } from '@/app/components/ui/progress';
import { formatDate, getStatusColor } from '@/utils';

export default function EventRegistrations() {
  const { id } = useParams<{ id: string }>();
  const eventId = Number(id);
  const { data: event } = useEvent(eventId);
  const { data: registrations, isLoading } = useRegistrationsByEvent(eventId);

  const pct = event ? Math.min(100, ((event.registered_count ?? 0) / event.max_attendees) * 100) : 0;

  return (
    <div>
      <PageHeader
        title="Event Registrations"
        description={event?.title}
      />

      {event && (
        <div className="bg-card border border-border rounded-xl p-5 mb-6 flex items-center gap-6">
          <div>
            <p className="text-sm text-muted-foreground">Capacity</p>
            <p className="text-2xl font-bold">{(event.registered_count ?? 0)} / {event.max_attendees}</p>
          </div>
          <div className="flex-1">
            <Progress value={pct} className="h-2.5" />
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Fill rate</p>
            <p className="text-xl font-bold">{Math.round(pct)}%</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-xl" />)}</div>
      ) : !registrations?.length ? (
        <EmptyState icon={Users} title="No registrations yet" description="Registrations will appear here when users sign up." />
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">User</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Registered</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {registrations.map((reg) => (
                <tr key={reg.id} className="hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Avatar className="h-7 w-7">
                        <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                          {(reg.user?.full_name ?? reg.user?.username ?? 'U').slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{reg.user?.full_name ?? `User #${reg.user_id}`}</p>
                        <p className="text-xs text-muted-foreground">{reg.user?.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{formatDate(reg.registered_at)}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${getStatusColor(reg.status)}`}>
                      {reg.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
