drop table if exists charities;
create table charities (
  id integer primary key autoincrement,
  name text not null,
  email text not null,
  regNo integer not null,
  postCode text,
  address text,
  description text,
  password text
);