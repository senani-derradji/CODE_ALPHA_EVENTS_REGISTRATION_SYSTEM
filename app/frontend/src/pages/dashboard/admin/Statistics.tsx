import { useAdminStats } from '@/hooks/useAdmin';
import PageHeader from '@/components/PageHeader';
import StatCard from '@/components/StatCard';
import { Users, Calendar, ClipboardList, Building, Shield, Activity } from 'lucide-react';
import { Skeleton } from '@/app/components/ui/skeleton';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area,
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

export default function AdminStatistics() {
  const { data: stats, isLoading } = useAdminStats();

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Statistics" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
        </div>
      </div>
    );
  }

  const roleData = stats?.users_by_role?.map((r) => ({
    name: r.role.charAt(0).toUpperCase() + r.role.slice(1),
    value: r.count,
  })) ?? [];

  const statusData = stats?.registration_status_counts?.map((r) => ({
    name: r.status.charAt(0).toUpperCase() + r.status.slice(1),
    value: r.count,
  })) ?? [];

  const topEventsData = stats?.top_events?.slice(0, 8).map((e) => ({
    name: e.title.length > 18 ? e.title.slice(0, 18) + '…' : e.title,
    registered: (e.registered_count ?? 0),
    capacity: e.max_attendees,
  })) ?? [];

  return (
    <div>
      <PageHeader title="System Statistics" description="Comprehensive platform analytics" />

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <StatCard title="Total Users" value={stats?.total_users ?? 0} icon={Users} color="indigo" index={0} />
        <StatCard title="Total Events" value={stats?.total_events ?? 0} icon={Calendar} color="violet" index={1} />
        <StatCard title="Total Registrations" value={stats?.total_registrations ?? 0} icon={ClipboardList} color="emerald" index={2} />
        <StatCard title="Active Users" value={stats?.active_users ?? 0} icon={Activity} color="emerald" index={3} />
        <StatCard title="Organizations" value={stats?.total_organizations ?? 0} icon={Building} color="amber" index={4} />
        <StatCard title="Admins" value={stats?.total_admins ?? 0} icon={Shield} color="rose" index={5} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold mb-4" style={{ fontFamily: 'var(--font-display)' }}>Users by Role</h3>
          {roleData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={roleData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {roleData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">No data</div>}
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold mb-4" style={{ fontFamily: 'var(--font-display)' }}>Registration Statuses</h3>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8 }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">No data</div>}
        </div>
      </div>

      {topEventsData.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold mb-4" style={{ fontFamily: 'var(--font-display)' }}>Top Events</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={topEventsData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
              <YAxis tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
              <Tooltip contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8 }} />
              <Bar dataKey="registered" name="Registered" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="capacity" name="Capacity" fill="#e0e7ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
