import apiClient from '@/services/api';
import type {
  AuthTokens,
  LoginPayload,
  RegisterPayload,
  ForgotPasswordPayload,
  ResetPasswordPayload,
  User,
} from '@/types';

export const authApi = {
  login: async (payload: LoginPayload): Promise<AuthTokens> => {
    const form = new URLSearchParams();
    form.append('username', payload.email);
    form.append('password', payload.password);
    const { data } = await apiClient.post<AuthTokens>('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },

  register: async (payload: RegisterPayload): Promise<User> => {
    const { data } = await apiClient.post<User>('/users/create/', payload);
    return data;
  },

  requestPasswordReset: async (payload: ForgotPasswordPayload) => {
    const { data } = await apiClient.post('/auth/request-password-reset', payload);
    return data;
  },

  resetPassword: async (payload: ResetPasswordPayload) => {
    const { data } = await apiClient.post('/auth/reset-password-submit', payload);
    return data;
  },

  activateUser: async (token: string) => {
    const { data } = await apiClient.get(`/auth/activate_user/${token}`);
    return data;
  },

  googleAuth: () => {
    window.location.href = 'http://localhost:8000/auth/google';
  },

  microsoftAuth: () => {
    window.location.href = 'http://localhost:8000/auth/microsoft';
  },
};
