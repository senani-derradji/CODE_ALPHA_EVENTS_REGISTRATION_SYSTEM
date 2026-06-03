import { createBrowserRouter } from 'react-router';

import PublicLayout from '@/layouts/PublicLayout';
import AuthRoot from '@/layouts/AuthRoot';
import AuthLayout from '@/layouts/AuthLayout';
import DashboardRoot from '@/layouts/DashboardRoot';
import DashboardLayout from '@/layouts/DashboardLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import OrgRoleGuard from '@/components/OrgRoleGuard';
import AdminRoleGuard from '@/components/AdminRoleGuard';

import Home from '@/pages/Home';
import EventsListing from '@/pages/EventsListing';
import EventDetails from '@/pages/EventDetails';
import NotFound from '@/pages/NotFound';

import Login from '@/pages/auth/Login';
import Register from '@/pages/auth/Register';
import ForgotPassword from '@/pages/auth/ForgotPassword';
import ResetPassword from '@/pages/auth/ResetPassword';

import UserOverview from '@/pages/dashboard/user/Overview';
import MyRegistrations from '@/pages/dashboard/user/MyRegistrations';
import Profile from '@/pages/dashboard/user/Profile';

import OrgOverview from '@/pages/dashboard/org/Overview';
import MyEvents from '@/pages/dashboard/org/MyEvents';
import CreateEvent from '@/pages/dashboard/org/CreateEvent';
import EditEvent from '@/pages/dashboard/org/EditEvent';
import EventRegistrations from '@/pages/dashboard/org/EventRegistrations';
import OrgAnalytics from '@/pages/dashboard/org/Analytics';

import AdminOverview from '@/pages/dashboard/admin/Overview';
import AdminUsers from '@/pages/dashboard/admin/Users';
import AdminOrganizations from '@/pages/dashboard/admin/Organizations';
import AdminEvents from '@/pages/dashboard/admin/Events';
import AdminRegistrations from '@/pages/dashboard/admin/Registrations';
import AdminStatistics from '@/pages/dashboard/admin/Statistics';

export const router = createBrowserRouter([
  {
    Component: PublicLayout,
    children: [
      { index: true, Component: Home },
      { path: 'events', Component: EventsListing },
      { path: 'events/:id', Component: EventDetails },
      { path: '*', Component: NotFound },
    ],
  },

  {
    Component: AuthRoot,
    children: [
      {
        path: 'auth',
        Component: AuthLayout,
        children: [
          { path: 'login', Component: Login },
          { path: 'register', Component: Register },
          { path: 'forgot-password', Component: ForgotPassword },
          { path: 'reset-password', Component: ResetPassword },
        ],
      },
    ],
  },

  {
    Component: DashboardRoot,
    children: [
      {
        Component: ProtectedRoute,
        children: [
          {
            path: 'dashboard',
            Component: DashboardLayout,
            children: [
              {
                path: 'user',
                children: [
                  { index: true, Component: UserOverview },
                  { path: 'registrations', Component: MyRegistrations },
                  { path: 'profile', Component: Profile },
                ],
              },

              {
                Component: OrgRoleGuard,
                children: [
                  {
                    path: 'org',
                    children: [
                      { index: true, Component: OrgOverview },
                      { path: 'events', Component: MyEvents },
                      { path: 'events/new', Component: CreateEvent },
                      { path: 'events/:id/edit', Component: EditEvent },
                      { path: 'events/:id/registrations', Component: EventRegistrations },
                      { path: 'analytics', Component: OrgAnalytics },
                    ],
                  },
                ],
              },

              {
                Component: AdminRoleGuard,
                children: [
                  {
                    path: 'admin',
                    children: [
                      { index: true, Component: AdminOverview },
                      { path: 'users', Component: AdminUsers },
                      { path: 'organizations', Component: AdminOrganizations },
                      { path: 'events', Component: AdminEvents },
                      { path: 'registrations', Component: AdminRegistrations },
                      { path: 'statistics', Component: AdminStatistics },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
]);
