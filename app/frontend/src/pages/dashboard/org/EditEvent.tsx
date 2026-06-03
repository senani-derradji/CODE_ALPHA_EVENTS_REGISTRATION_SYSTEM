import { useParams, useNavigate } from 'react-router';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useEffect } from 'react';
import { useEvent, useUpdateEvent } from '@/hooks/useEvents';
import PageHeader from '@/components/PageHeader';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Textarea } from '@/app/components/ui/textarea';
import { Skeleton } from '@/app/components/ui/skeleton';

const schema = z.object({
  title: z.string().min(3),
  description: z.string().min(10),
  location: z.string().min(2),
  start_time: z.string().min(1),
  end_time: z.string().min(1),
  max_attendees: z.coerce.number().int().min(1),
});
type FormData = z.infer<typeof schema>;

function toDatetimeLocal(iso: string) {
  try { return iso.slice(0, 16); } catch { return ''; }
}

export default function EditEvent() {
  const { id } = useParams<{ id: string }>();
  const eventId = Number(id);
  const navigate = useNavigate();
  const { data: event, isLoading } = useEvent(eventId);
  const { mutate: update, isPending } = useUpdateEvent();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  useEffect(() => {
    if (event) {
      reset({
        title: event.title,
        description: event.description,
        location: event.location,
        start_time: toDatetimeLocal(event.start_time),
        end_time: toDatetimeLocal(event.end_time),
        max_attendees: event.max_attendees,
      });
    }
  }, [event, reset]);

  const onSubmit = (data: FormData) => {
    update({ id: eventId, payload: data }, { onSuccess: () => navigate('/dashboard/org/events') });
  };

  if (isLoading) return <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 rounded-lg" />)}</div>;

  return (
    <div>
      <PageHeader title="Edit Event" description={`Editing: ${event?.title}`} />
      <div className="max-w-2xl">
        <div className="bg-card border border-border rounded-xl p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <Label>Event Title</Label>
              <Input {...register('title')} className="mt-1" />
              {errors.title && <p className="text-destructive text-xs mt-1">{errors.title.message}</p>}
            </div>
            <div>
              <Label>Description</Label>
              <Textarea {...register('description')} className="mt-1 resize-none" rows={5} />
              {errors.description && <p className="text-destructive text-xs mt-1">{errors.description.message}</p>}
            </div>
            <div>
              <Label>Location</Label>
              <Input {...register('location')} className="mt-1" />
              {errors.location && <p className="text-destructive text-xs mt-1">{errors.location.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Start Date & Time</Label>
                <Input {...register('start_time')} type="datetime-local" className="mt-1" />
                {errors.start_time && <p className="text-destructive text-xs mt-1">{errors.start_time.message}</p>}
              </div>
              <div>
                <Label>End Date & Time</Label>
                <Input {...register('end_time')} type="datetime-local" className="mt-1" />
                {errors.end_time && <p className="text-destructive text-xs mt-1">{errors.end_time.message}</p>}
              </div>
            </div>
            <div className="max-w-48">
              <Label>Max Attendees</Label>
              <Input {...register('max_attendees')} type="number" min={1} className="mt-1" />
              {errors.max_attendees && <p className="text-destructive text-xs mt-1">{errors.max_attendees.message}</p>}
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={isPending}>{isPending ? 'Saving…' : 'Save Changes'}</Button>
              <Button type="button" variant="outline" onClick={() => navigate('/dashboard/org/events')}>Cancel</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
