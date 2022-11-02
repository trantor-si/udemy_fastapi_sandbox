drop table if exists users;

create table users (
	id serial,
	email varchar(200) default NULL,
	username varchar(45) default NULL,
	first_name varchar(45) default NULL,
	last_name varchar(45) default NULL,
	hashed_password varchar(200) default NULL,
	is_active boolean default NULL,
	
	primary key (id)
);

drop table if exists todos;

create table todos (
	id serial,
	title varchar(200) default NULL,
	description varchar(200) default NULL,
	priority integer default NULL,
	complete integer default NULL,
	owner_id integer default NULL,
	
	primary key (id),
	foreign key (owner_id) references users(id)
);