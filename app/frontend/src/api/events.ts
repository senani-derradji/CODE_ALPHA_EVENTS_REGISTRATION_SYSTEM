import apiClient from '@/services/api';
import type { Event, CreateEventPayload, UpdateEventPayload } from '@/types';

export const eventsApi = {
  getEvents: async (): Promise<Event[]> => {
    const { data } = await apiClient.get<Event[]>('/events/get_events/');
    return data;
  },

  getEvent: async (id: number): Promise<Event> => {
    const { data } = await apiClient.get<Event>(`/events/get_event/${id}`);
    return data;
  },

  createEvent: async (payload: CreateEventPayload): Promise<Event> => {
    const { data } = await apiClient.post<Event>('/events/create/', payload);
    return data;
  },

  updateEvent: async (id: number, payload: UpdateEventPayload): Promise<Event> => {
    const { data } = await apiClient.put<Event>(`/events/update_event/${id}`, payload);
    return data;
  },

  deleteEvent: async (id: number): Promise<void> => {
    await apiClient.delete(`/events/delete_event/${id}`);
  },

  getEventsByOrganizer: async (id: number): Promise<Event[]> => {
    const { data } = await apiClient.get<Event[]>(`/events/get_events_by_organizer/${id}`);
    return data;
  },

  countEvents: async (): Promise<number> => {
    const { data } = await apiClient.get<number>('/events/count_events/');
    return data;
  },
};
