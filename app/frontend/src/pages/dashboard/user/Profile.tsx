import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/store/AuthContext';
import { useUpdateUser } from '@/hooks/useUsers';
import PageHeader from '@/components/PageHeader';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Textarea } from '@/app/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/app/components/ui/avatar';
import { Badge } from '@/app/components/ui/badge';
import { getRoleLabel } from '@/utils';

const schema = z.object({
  full_name: z.string().min(2, 'Name too short'),
  bio: z.string().max(300).optional(),
  phone: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const { mutate: update, isPending } = useUpdateUser();

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: user?.full_name ?? '',
      bio: user?.bio ?? '',
      phone: user?.phone ?? '',
    },
  });

  const onSubmit = (data: FormData) => {
    update({ id: user!.id, payload: data }, { onSuccess: refreshUser });
  };

  const roleColor = user?.role === 'admin'
    ? 'bg-rose-100 text-rose-700 dark:bg-rose-900 dark:text-rose-300'
    : user?.role === 'organization'
    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
    : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300';

  return (
    <div>
      <PageHeader title="My Profile" description="Manage your account information" />

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-card border border-border rounded-xl p-6 flex flex-col items-center text-center">
          <Avatar className="w-20 h-20 mb-4">
            <AvatarFallback className="bg-primary text-primary-foreground text-2xl font-bold">
              {user?.full_name?.slice(0, 2).toUpperCase() ?? 'U'}
            </AvatarFallback>
          </Avatar>
          <p className="font-semibold text-lg">{user?.full_name}</p>
          <p className="text-sm text-muted-foreground mb-3">@{user?.username}</p>
          <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${roleColor}`}>
            {getRoleLabel(user?.role ?? 'user')}
          </span>
          {user?.is_verified && (
            <Badge variant="secondary" className="mt-2 text-xs">Verified</Badge>
          )}
          {!user?.is_active && (
            <Badge variant="destructive" className="mt-2 text-xs">Inactive</Badge>
          )}
        </div>

        <div className="md:col-span-2 bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-5" style={{ fontFamily: 'var(--font-display)' }}>Edit Profile</h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label>Email</Label>
              <Input value={user?.email ?? ''} disabled className="mt-1 bg-muted/50" />
            </div>
            <div>
              <Label>Full name</Label>
              <Input {...register('full_name')} className="mt-1" />
              {errors.full_name && <p className="text-destructive text-xs mt-1">{errors.full_name.message}</p>}
            </div>
            <div>
              <Label>Phone</Label>
              <Input {...register('phone')} placeholder="+1 (555) 000-0000" className="mt-1" />
            </div>
            <div>
              <Label>Bio</Label>
              <Textarea {...register('bio')} placeholder="Tell us about yourself…" className="mt-1 resize-none" rows={3} />
              {errors.bio && <p className="text-destructive text-xs mt-1">{errors.bio.message}</p>}
            </div>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Saving…' : 'Save changes'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
