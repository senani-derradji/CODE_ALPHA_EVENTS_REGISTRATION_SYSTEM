import apiClient from '@/services/api';
import type { User, UpdateProfilePayload } from '@/types';

export const usersApi = {
  getUsers: async (): Promise<User[]> => {
    const { data } = await apiClient.get<User[]>('/users/get_users/');
    return data;
  },

  getUser: async (id: number): Promise<User> => {
    const { data } = await apiClient.get<User>(`/users/get_user/${id}`);
    return data;
  },

  updateUser: async (id: number, payload: UpdateProfilePayload): Promise<User> => {
    const { data } = await apiClient.put<User>(`/users/update_user/${id}`, payload);
    return data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/delete_user/${id}`);
  },

  promoteToOrganization: async (id: number): Promise<User> => {
    const { data } = await apiClient.put<User>(`/users/promote_to_organization/${id}`);
    return data;
  },
};
