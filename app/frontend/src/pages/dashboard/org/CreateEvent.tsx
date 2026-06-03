import { useNavigate } from 'react-router';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { CalendarPlus } from 'lucide-react';
import { useCreateEvent } from '@/hooks/useEvents';
import PageHeader from '@/components/PageHeader';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Textarea } from '@/app/components/ui/textarea';

const schema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  location: z.string().min(2, 'Location is required'),
  start_time: z.string().min(1, 'Start date is required'),
  end_time: z.string().min(1, 'End date is required'),
  max_attendees: z.coerce.number().int().min(1, 'Capacity must be at least 1'),
}).refine((d) => new Date(d.end_time) > new Date(d.start_time), {
  message: 'End date must be after start date',
  path: ['end_time'],
});
type FormData = z.infer<typeof schema>;

export default function CreateEvent() {
  const navigate = useNavigate();
  const { mutate: create, isPending } = useCreateEvent();

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    create(data, { onSuccess: () => navigate('/dashboard/org/events') });
  };

  return (
    <div>
      <PageHeader title="Create Event" description="Set up a new event for registration" />

      <div className="max-w-2xl">
        <div className="bg-card border border-border rounded-xl p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <Label>Event Title *</Label>
              <Input {...register('title')} placeholder="Tech Conference 2024" className="mt-1" />
              {errors.title && <p className="text-destructive text-xs mt-1">{errors.title.message}</p>}
            </div>
            <div>
              <Label>Description *</Label>
              <Textarea {...register('description')} placeholder="Describe your event…" className="mt-1 resize-none" rows={5} />
              {errors.description && <p className="text-destructive text-xs mt-1">{errors.description.message}</p>}
            </div>
            <div>
              <Label>Location *</Label>
              <Input {...register('location')} placeholder="San Francisco, CA or Online" className="mt-1" />
              {errors.location && <p className="text-destructive text-xs mt-1">{errors.location.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Start Date & Time *</Label>
                <Input {...register('start_time')} type="datetime-local" className="mt-1" />
                {errors.start_time && <p className="text-destructive text-xs mt-1">{errors.start_time.message}</p>}
              </div>
              <div>
                <Label>End Date & Time *</Label>
                <Input {...register('end_time')} type="datetime-local" className="mt-1" />
                {errors.end_time && <p className="text-destructive text-xs mt-1">{errors.end_time.message}</p>}
              </div>
            </div>
            <div className="max-w-48">
              <Label>Max Attendees *</Label>
              <Input {...register('max_attendees')} type="number" min={1} placeholder="100" className="mt-1" />
              {errors.max_attendees && <p className="text-destructive text-xs mt-1">{errors.max_attendees.message}</p>}
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Creating…' : <><CalendarPlus className="w-4 h-4 mr-2" /> Create Event</>}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate('/dashboard/org/events')}>
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
