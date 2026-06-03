import { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, Lock } from 'lucide-react';
import { authApi } from '@/api/auth';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { toast } from 'sonner';

const schema = z.object({
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});
type FormData = z.infer<typeof schema>;

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const navigate = useNavigate();
  const [showPass, setShowPass] = useState(false);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await authApi.resetPassword({ ...data, token });
      toast.success('Password reset successfully!');
      navigate('/auth/login');
    } catch {
      toast.error('Failed to reset password. The link may have expired.');
    }
  };

  if (!token) {
    return (
      <div className="text-center">
        <p className="text-muted-foreground">Invalid or missing reset token.</p>
        <Link to="/auth/forgot-password" className="text-primary hover:underline text-sm mt-4 block">Request a new link</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
        <Lock className="w-6 h-6 text-primary" />
      </div>
      <h2 className="font-bold mb-1" style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem' }}>Reset password</h2>
      <p className="text-muted-foreground mb-8">Enter your new password below</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <Label htmlFor="new_password">New password</Label>
          <div className="relative mt-1">
            <Input id="new_password" type={showPass ? 'text' : 'password'} placeholder="Min. 8 characters" className="pr-10" {...register('new_password')} />
            <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" onClick={() => setShowPass((v) => !v)}>
              {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.new_password && <p className="text-destructive text-xs mt-1">{errors.new_password.message}</p>}
        </div>
        <div>
          <Label htmlFor="confirm_password">Confirm password</Label>
          <Input id="confirm_password" type="password" placeholder="Repeat password" className="mt-1" {...register('confirm_password')} />
          {errors.confirm_password && <p className="text-destructive text-xs mt-1">{errors.confirm_password.message}</p>}
        </div>
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? 'Resetting…' : 'Reset password'}
        </Button>
      </form>
      <p className="text-center text-sm text-muted-foreground mt-6">
        <Link to="/auth/login" className="text-primary hover:underline font-medium">Back to sign in</Link>
      </p>
    </div>
  );
}
