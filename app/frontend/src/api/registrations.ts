import apiClient from '@/services/api';
import type { Registration } from '@/types';

export const registrationsApi = {
  create: async (eventId: number): Promise<Registration> => {
    const { data } = await apiClient.post<Registration>(`/registrations/create/?event_id=${eventId}`);
    return data;
  },

  getRegistrations: async (): Promise<Registration[]> => {
    const { data } = await apiClient.get<Registration[]>('/registrations/get_registrations/');
    return data;
  },

  getRegistrationsByUser: async (userId: number): Promise<Registration[]> => {
    const { data } = await apiClient.get<Registration[]>(`/registrations/get_registrations_by_user/${userId}`);
    return data;
  },

  getRegistrationsByEvent: async (eventId: number): Promise<Registration[]> => {
    const { data } = await apiClient.get<Registration[]>(`/registrations/get_registrations_by_event/${eventId}`);
    return data;
  },

  getRegistration: async (id: number): Promise<Registration> => {
    const { data } = await apiClient.get<Registration>(`/registrations/get_registration/${id}`);
    return data;
  },

  cancelRegistration: async (id: number): Promise<void> => {
    await apiClient.delete(`/registrations/cancel_registration/${id}`);
  },
};
