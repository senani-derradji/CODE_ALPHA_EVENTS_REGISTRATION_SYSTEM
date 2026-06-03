export type UserRole = 'user' | 'organization' | 'admin';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  profile_picture?: string;
  bio?: string;
  phone?: string;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

// Backend UserCreate only accepts username, email, password
export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  token: string;
  new_password: string;
  confirm_password: string;
}

// Backend event fields: start_time, end_time, max_attendees
export interface Event {
  id: number;
  title: string;
  description: string;
  location: string;
  start_time: string;   // backend field
  end_time: string;     // backend field
  max_attendees: number; // backend field
  organizer_id?: number;
  organizer?: User;
  // Optional fields that may not exist in backend response
  registered_count?: number;
  image_url?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateEventPayload {
  title: string;
  description: string;
  location: string;
  start_time: string;   // must match backend
  end_time: string;     // must match backend
  max_attendees: number; // must match backend
}

export interface UpdateEventPayload extends Partial<CreateEventPayload> {}

export type RegistrationStatus = 'confirmed' | 'pending' | 'cancelled';

export interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  status: RegistrationStatus;
  registered_at: string;
  user?: User;
  event?: Event;
}

export interface AdminStats {
  total_users: number;
  total_events: number;
  total_registrations: number;
  active_users: number;
  inactive_users: number;
  total_organizations: number;
  total_admins: number;
  top_events: TopEvent[];
  registration_status_counts: RegistrationStatusCount[];
  users_by_role: UsersByRole[];
}

export interface TopEvent {
  id: number;
  title: string;
  registered_count: number;
  capacity: number;
}

export interface RegistrationStatusCount {
  status: RegistrationStatus;
  count: number;
}

export interface UsersByRole {
  role: UserRole;
  count: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface UpdateUserRolePayload {
  role: UserRole;
}

export interface UpdateProfilePayload {
  full_name?: string;
  bio?: string;
  phone?: string;
  profile_picture?: string;
}
