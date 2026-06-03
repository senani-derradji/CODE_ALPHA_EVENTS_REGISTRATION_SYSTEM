import { useAuth } from '@/store/AuthContext';
import { useEventsByOrganizer } from '@/hooks/useEvents';
import { useRegistrations } from '@/hooks/useRegistrations';
import PageHeader from '@/components/PageHeader';
import StatCard from '@/components/StatCard';
import { BarChart3, Users, TrendingUp, Calendar } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'];

export default function OrgAnalytics() {
  const { user } = useAuth();
  const { data: events } = useEventsByOrganizer(user?.id ?? 0);
  const { data: allRegs } = useRegistrations();

  const myEventIds = new Set(events?.map((e) => e.id) ?? []);
  const myRegs = allRegs?.filter((r) => myEventIds.has(r.event_id)) ?? [];

  const eventBarData = events?.slice(0, 8).map((e) => ({
    name: e.title.length > 16 ? e.title.slice(0, 16) + '…' : e.title,
    registered: (e.registered_count ?? 0),
    capacity: e.max_attendees,
  })) ?? [];

  const statusData = [
    { name: 'Confirmed', value: myRegs.filter((r) => r.status === 'confirmed').length },
    { name: 'Pending', value: myRegs.filter((r) => r.status === 'pending').length },
    { name: 'Cancelled', value: myRegs.filter((r) => r.status === 'cancelled').length },
  ].filter((d) => d.value > 0);

  const totalCap = events?.reduce((s, e) => s + e.max_attendees, 0) ?? 0;
  const totalReg = events?.reduce((s, e) => s + (e.registered_count ?? 0), 0) ?? 0;
  const fillRate = totalCap > 0 ? Math.round((totalReg / totalCap) * 100) : 0;

  return (
    <div>
      <PageHeader title="Analytics" description="Insights into your events performance" />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Events" value={events?.length ?? 0} icon={Calendar} color="indigo" index={0} />
        <StatCard title="Total Registrations" value={totalReg} icon={Users} color="violet" index={1} />
        <StatCard title="Fill Rate" value={`${fillRate}%`} icon={TrendingUp} color="emerald" index={2} />
        <StatCard title="Available Spots" value={totalCap - totalReg} icon={BarChart3} color="amber" index={3} />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold mb-4" style={{ fontFamily: 'var(--font-display)' }}>Registrations per Event</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={eventBarData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
              <YAxis tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
              <Tooltip contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8 }} />
              <Bar dataKey="registered" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="capacity" fill="#e0e7ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold mb-4" style={{ fontFamily: 'var(--font-display)' }}>Registration Status</h3>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={statusData} cx="50%" cy="45%" outerRadius={90} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">No data yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
