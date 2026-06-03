import { useState } from 'react';
import { Building, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import { useUsers } from '@/hooks/useUsers';
import { useActivateUser, useDeactivateUser } from '@/hooks/useAdmin';
import { adminApi } from '@/api/admin';
import { useQueryClient } from '@tanstack/react-query';
import { userKeys } from '@/hooks/useUsers';
import PageHeader from '@/components/PageHeader';
import SearchBar from '@/components/SearchBar';
import EmptyState from '@/components/EmptyState';
import { Avatar, AvatarFallback } from '@/app/components/ui/avatar';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { formatDate } from '@/utils';
import { toast } from 'sonner';

export default function AdminOrganizations() {
  const { data: users, isLoading } = useUsers();
  const [search, setSearch] = useState('');
  const qc = useQueryClient();

  const orgs = (users ?? []).filter((u) => u.role === 'organization');
  const filtered = orgs.filter((u) =>
    !search || u.full_name?.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())
  );

  const promote = async (id: number) => {
    try {
      await adminApi.promoteOrganization(id);
      qc.invalidateQueries({ queryKey: userKeys.all });
      toast.success('Promoted to organization');
    } catch { toast.error('Failed to promote'); }
  };

  const demote = async (id: number) => {
    try {
      await adminApi.demoteOrganization(id);
      qc.invalidateQueries({ queryKey: userKeys.all });
      toast.success('Demoted from organization');
    } catch { toast.error('Failed to demote'); }
  };

  return (
    <div>
      <PageHeader title="Organizations" description={`${orgs.length} organizations`} />

      <div className="mb-4">
        <SearchBar value={search} onChange={setSearch} placeholder="Search organizations…" />
      </div>

      {isLoading ? (
        <div className="space-y-2">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={Building} title="No organizations" description="No users with organization role." />
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Organization</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground hidden md:table-cell">Joined</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((org) => (
                <tr key={org.id} className="hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 text-xs">
                          {(org.full_name ?? org.username ?? 'O').slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{org.full_name ?? org.username}</p>
                        <p className="text-xs text-muted-foreground">{org.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground hidden md:table-cell">{formatDate(org.created_at)}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${org.is_active ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400' : 'bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-400'}`}>
                      {org.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center gap-2 justify-end">
                      <Button variant="outline" size="sm" onClick={() => demote(org.id)}>
                        <ArrowDownCircle className="w-3.5 h-3.5 mr-1" /> Demote
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
