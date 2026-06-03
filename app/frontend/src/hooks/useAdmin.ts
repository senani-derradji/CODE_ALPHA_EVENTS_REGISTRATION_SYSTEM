import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi } from '@/api/admin';
import { userKeys } from './useUsers';
import type { UserRole } from '@/types';
import { toast } from 'sonner';

export const adminKeys = {
  stats: ['admin', 'stats'] as const,
};

export function useAdminStats() {
  return useQuery({ queryKey: adminKeys.stats, queryFn: adminApi.getStats });
}

export function useUpdateUserRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, role }: { id: number; role: UserRole }) =>
      adminApi.updateUserRole(id, role),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: userKeys.all });
      toast.success('User role updated');
    },
    onError: () => toast.error('Failed to update role'),
  });
}

export function useActivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => adminApi.activateUser(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: userKeys.all });
      toast.success('User activated');
    },
    onError: () => toast.error('Failed to activate user'),
  });
}

export function useDeactivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => adminApi.deactivateUser(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: userKeys.all });
      toast.success('User deactivated');
    },
    onError: () => toast.error('Failed to deactivate user'),
  });
}
