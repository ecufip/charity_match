drop table if exists charities;
create table charities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  description TEXT,
  password TEXT NOT NULL
);

drop table if exists projects;
create table projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  charityId INTEGER NOT NULL,
  short TEXT,
  description TEXT,
  picUrl TEXT NOT NULL,
  FOREIGN KEY (charityId) REFERENCES charities(id)
);