-- Template for a user-owned table with RLS
-- Replace {table} and columns as needed
-- Example usage: replace {table} with documents

-- create extension if not exists pgcrypto; -- if you need gen_random_uuid in older versions

create table if not exists public.{table} (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamp with time zone default now()
);

alter table public.{table} enable row level security;

create policy if not exists {table}_select_own
on public.{table} for select to authenticated
using (owner_id = auth.uid());

create policy if not exists {table}_insert_own
on public.{table} for insert to authenticated
with check (owner_id = auth.uid());

create policy if not exists {table}_update_own
on public.{table} for update to authenticated
using (owner_id = auth.uid())
with check (owner_id = auth.uid());

create policy if not exists {table}_delete_own
on public.{table} for delete to authenticated
using (owner_id = auth.uid());

-- Optional: admin can read all
-- create policy if not exists {table}_admin_read_all
-- on public.{table} for select to authenticated
-- using (exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'));
