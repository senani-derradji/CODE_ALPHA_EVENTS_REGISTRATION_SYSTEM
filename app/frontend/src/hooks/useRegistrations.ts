import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { registrationsApi } from '@/api/registrations';
import { toast } from 'sonner';

export const regKeys = {
  all: ['registrations'] as const,
  list: () => [...regKeys.all, 'list'] as const,
  byUser: (id: number) => [...regKeys.all, 'user', id] as const,
  byEvent: (id: number) => [...regKeys.all, 'event', id] as const,
  detail: (id: number) => [...regKeys.all, 'detail', id] as const,
};

export function useRegistrations() {
  return useQuery({ queryKey: regKeys.list(), queryFn: registrationsApi.getRegistrations });
}

export function useRegistrationsByUser(userId: number) {
  return useQuery({
    queryKey: regKeys.byUser(userId),
    queryFn: () => registrationsApi.getRegistrationsByUser(userId),
    enabled: !!userId,
  });
}

export function useRegistrationsByEvent(eventId: number) {
  return useQuery({
    queryKey: regKeys.byEvent(eventId),
    queryFn: () => registrationsApi.getRegistrationsByEvent(eventId),
    enabled: !!eventId,
  });
}

export function useRegisterForEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (eventId: number) => registrationsApi.create(eventId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: regKeys.all });
      toast.success('Successfully registered for event!');
    },
    onError: () => toast.error('Failed to register for event'),
  });
}

export function useCancelRegistration() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => registrationsApi.cancelRegistration(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: regKeys.all });
      toast.success('Registration cancelled');
    },
    onError: () => toast.error('Failed to cancel registration'),
  });
}
