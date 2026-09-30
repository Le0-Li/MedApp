-- Table structure only. Demo/seed data lives in 001_seed.sql instead, so
-- that structure-only migrations can be applied on their own to other
-- databases (see 000_test_db.sql, which sets up a dedicated, empty test
-- database using just this file plus 002 and 003).

create table doctors (
  id bigserial primary key,
  full_name text not null,
  specialty text not null,
  created_at timestamp with time zone not null default now()
);

create table doctor_availabilities (
  id bigserial primary key,
  doctor_id bigint not null references doctors(id) on delete cascade,
  starts_at timestamp with time zone not null,
  ends_at timestamp with time zone not null,
  created_at timestamp with time zone not null default now()
);
