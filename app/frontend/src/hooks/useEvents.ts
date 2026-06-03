import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { eventsApi } from '@/api/events';
import type { CreateEventPayload, UpdateEventPayload } from '@/types';
import { toast } from 'sonner';

export const eventKeys = {
  all: ['events'] as const,
  list: () => [...eventKeys.all, 'list'] as const,
  detail: (id: number) => [...eventKeys.all, 'detail', id] as const,
  byOrganizer: (id: number) => [...eventKeys.all, 'organizer', id] as const,
};

export function useEvents() {
  return useQuery({ queryKey: eventKeys.list(), queryFn: eventsApi.getEvents });
}

export function useEvent(id: number) {
  return useQuery({
    queryKey: eventKeys.detail(id),
    queryFn: () => eventsApi.getEvent(id),
    enabled: !!id,
  });
}

export function useEventsByOrganizer(id: number) {
  return useQuery({
    queryKey: eventKeys.byOrganizer(id),
    queryFn: () => eventsApi.getEventsByOrganizer(id),
    enabled: !!id,
  });
}

export function useCreateEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateEventPayload) => eventsApi.createEvent(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: eventKeys.all });
      toast.success('Event created successfully');
    },
    onError: () => toast.error('Failed to create event'),
  });
}

export function useUpdateEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: UpdateEventPayload }) =>
      eventsApi.updateEvent(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: eventKeys.all });
      toast.success('Event updated successfully');
    },
    onError: () => toast.error('Failed to update event'),
  });
}

export function useDeleteEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => eventsApi.deleteEvent(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: eventKeys.all });
      toast.success('Event deleted');
    },
    onError: () => toast.error('Failed to delete event'),
  });
}
