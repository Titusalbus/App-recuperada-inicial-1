-- Profiles table to hold roles; RLS so each user sees only their row
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'user' check (role in ('user','admin')),
  created_at timestamp with time zone default now()
);

alter table public.profiles enable row level security;

-- Each user can read/update only their own profile
create policy if not exists read_own_profile
on public.profiles for select to authenticated
using (id = auth.uid());

create policy if not exists update_own_profile
on public.profiles for update to authenticated
using (id = auth.uid())
with check (id = auth.uid());

-- Allow users to insert their own profile row (fallback if trigger hasn't run)
create policy if not exists insert_own_profile
on public.profiles for insert to authenticated
with check (id = auth.uid());

-- Auto-create profile on user signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id) values (new.id)
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

-- Attach trigger to auth.users
create trigger if not exists on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
