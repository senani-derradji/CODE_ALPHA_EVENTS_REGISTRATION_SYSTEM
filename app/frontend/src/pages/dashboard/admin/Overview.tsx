import { Users, Calendar, ClipboardList, Building, Shield, TrendingUp } from 'lucide-react';
import { Link } from 'react-router';
import { useAdminStats } from '@/hooks/useAdmin';
import StatCard from '@/components/StatCard';
import PageHeader from '@/components/PageHeader';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Progress } from '@/app/components/ui/progress';

export default function AdminOverview() {
  const { data: stats, isLoading } = useAdminStats();

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Admin Dashboard" description="Full system overview" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Admin Dashboard"
        description="Full system overview and management"
        action={<Button asChild><Link to="/dashboard/admin/statistics">View Statistics</Link></Button>}
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Users" value={stats?.total_users ?? 0} icon={Users} color="indigo" index={0} />
        <StatCard title="Total Events" value={stats?.total_events ?? 0} icon={Calendar} color="violet" index={1} />
        <StatCard title="Registrations" value={stats?.total_registrations ?? 0} icon={ClipboardList} color="emerald" index={2} />
        <StatCard title="Organizations" value={stats?.total_organizations ?? 0} icon={Building} color="amber" index={3} />
        <StatCard title="Active Users" value={stats?.active_users ?? 0} icon={TrendingUp} color="emerald" index={4} />
        <StatCard title="Inactive Users" value={stats?.inactive_users ?? 0} icon={Users} color="rose" index={5} />
        <StatCard title="Admins" value={stats?.total_admins ?? 0} icon={Shield} color="rose" index={6} />
        <StatCard
          title="Activity Rate"
          value={stats?.total_users ? `${Math.round((stats.active_users / stats.total_users) * 100)}%` : '0%'}
          icon={TrendingUp}
          color="indigo"
          index={7}
        />
      </div>

      {stats?.top_events && stats.top_events.length > 0 && (
        <div className="bg-card border border-border rounded-xl mb-6">
          <div className="px-5 py-4 border-b border-border">
            <h2 className="font-semibold" style={{ fontFamily: 'var(--font-display)' }}>Top Events by Registrations</h2>
          </div>
          <div className="p-5 space-y-3">
            {stats.top_events.map((event) => {
              const pct = Math.min(100, ((event.registered_count ?? 0) / event.max_attendees) * 100);
              return (
                <div key={event.id}>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium truncate flex-1 mr-4">{event.title}</p>
                    <p className="text-xs text-muted-foreground shrink-0">
                      {(event.registered_count ?? 0)} / {event.max_attendees}
                    </p>
                  </div>
                  <Progress value={pct} className="h-1.5" />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
