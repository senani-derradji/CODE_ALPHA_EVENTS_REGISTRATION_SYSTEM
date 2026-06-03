import { Link } from 'react-router';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail } from 'lucide-react';
import { authApi } from '@/api/auth';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { toast } from 'sonner';

const schema = z.object({ email: z.string().email('Enter a valid email') });
type FormData = z.infer<typeof schema>;

export default function ForgotPassword() {
  const { register, handleSubmit, formState: { errors, isSubmitting, isSubmitSuccessful } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await authApi.requestPasswordReset(data);
      toast.success('Reset link sent! Check your inbox.');
    } catch {
      toast.error('Failed to send reset link. Please try again.');
    }
  };

  if (isSubmitSuccessful) {
    return (
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center mx-auto mb-4">
          <Mail className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
        </div>
        <h2 className="font-bold mb-2" style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem' }}>Check your email</h2>
        <p className="text-muted-foreground mb-6">We sent a password reset link to your email address.</p>
        <Link to="/auth/login" className="text-primary hover:underline text-sm font-medium">Back to sign in</Link>
      </div>
    );
  }

  return (
    <div>
      <h2 className="font-bold mb-1" style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem' }}>Forgot password?</h2>
      <p className="text-muted-foreground mb-8">Enter your email to receive a reset link</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <Label htmlFor="email">Email address</Label>
          <Input id="email" type="email" placeholder="you@company.com" className="mt-1" {...register('email')} />
          {errors.email && <p className="text-destructive text-xs mt-1">{errors.email.message}</p>}
        </div>
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? 'Sending…' : 'Send reset link'}
        </Button>
      </form>
      <p className="text-center text-sm text-muted-foreground mt-6">
        <Link to="/auth/login" className="text-primary hover:underline font-medium">Back to sign in</Link>
      </p>
    </div>
  );
}
