import apiClient from '@/services/api';
import type { AdminStats, UserRole } from '@/types';

export const adminApi = {
  getStats: async (): Promise<AdminStats> => {
    const { data } = await apiClient.get<AdminStats>('/admin/stats');
    return data;
  },

  updateUserRole: async (id: number, role: UserRole) => {
    const { data } = await apiClient.put(`/admin/users/${id}/role`, { role });
    return data;
  },

  activateUser: async (id: number) => {
    const { data } = await apiClient.put(`/admin/users/${id}/activate`);
    return data;
  },

  deactivateUser: async (id: number) => {
    const { data } = await apiClient.put(`/admin/users/${id}/deactivate`);
    return data;
  },

  promoteOrganization: async (id: number) => {
    const { data } = await apiClient.post(`/admin/organizations/promote/${id}`);
    return data;
  },

  demoteOrganization: async (id: number) => {
    const { data } = await apiClient.post(`/admin/organizations/demote/${id}`);
    return data;
  },
};
