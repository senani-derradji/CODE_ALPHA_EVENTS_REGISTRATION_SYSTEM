import { useState, useMemo } from 'react';
import { motion } from 'motion/react';
import { SlidersHorizontal } from 'lucide-react';
import { useEvents } from '@/hooks/useEvents';
import { useRegistrationsByUser } from '@/hooks/useRegistrations';
import { useRegisterForEvent } from '@/hooks/useRegistrations';
import { useAuth } from '@/store/AuthContext';
import EventCard from '@/components/EventCard';
import SearchBar from '@/components/SearchBar';
import EmptyState from '@/components/EmptyState';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Calendar } from 'lucide-react';

export default function EventsListing() {
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('date_asc');
  const { data: events, isLoading } = useEvents();
  const { user } = useAuth();
  const { data: myRegs } = useRegistrationsByUser(user?.id ?? 0);
  const { mutate: register, isPending } = useRegisterForEvent();

  const registeredEventIds = useMemo(
    () => new Set(myRegs?.map((r) => r.event_id) ?? []),
    [myRegs]
  );

  const filtered = useMemo(() => {
    let list = events ?? [];
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (e) => e.title.toLowerCase().includes(q) || e.location.toLowerCase().includes(q) || e.description.toLowerCase().includes(q)
      );
    }
    switch (sort) {
      case 'date_asc': return [...list].sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
      case 'date_desc': return [...list].sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
      case 'capacity': return [...list].sort((a, b) => b.max_attendees - a.capacity);
      case 'popular': return [...list].sort((a, b) => (b.registered_count ?? 0) - a.registered_count);
      default: return list;
    }
  }, [events, search, sort]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-bold mb-1" style={{ fontFamily: 'var(--font-display)', fontSize: '2rem' }}>Browse Events</h1>
        <p className="text-muted-foreground mb-8">Discover and register for upcoming events</p>

        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <div className="flex-1">
            <SearchBar value={search} onChange={setSearch} placeholder="Search events, locations…" />
          </div>
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-muted-foreground" />
            <Select value={sort} onValueChange={setSort}>
              <SelectTrigger className="w-44">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date_asc">Date (earliest)</SelectItem>
                <SelectItem value="date_desc">Date (latest)</SelectItem>
                <SelectItem value="popular">Most popular</SelectItem>
                <SelectItem value="capacity">Most capacity</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {isLoading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-xl border border-border overflow-hidden">
                <Skeleton className="h-2" />
                <div className="p-5 space-y-3">
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-8 w-full mt-4" />
                </div>
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={Calendar}
            title="No events found"
            description={search ? `No events match "${search}". Try a different search.` : 'No events available yet.'}
          />
        ) : (
          <>
            <p className="text-sm text-muted-foreground mb-4">{filtered.length} event{filtered.length !== 1 ? 's' : ''} found</p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filtered.map((event, i) => (
                <EventCard
                  key={event.id}
                  event={event}
                  index={i}
                  onRegister={user ? (id) => register(id) : undefined}
                  isRegistering={isPending}
                  isRegistered={registeredEventIds.has(event.id)}
                />
              ))}
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}
