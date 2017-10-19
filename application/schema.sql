drop table if exists charities;
create table charities (
  id integer primary key autoincrement,
  name text not null,
  regNo integer not null,
  postCode text not null,
  address text not null,
  description text
);