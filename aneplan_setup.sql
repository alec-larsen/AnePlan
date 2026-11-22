create table if not exists tasks(
	name TEXT UNIQUE not null,
	parent INTEGER references tasks(name),
	weight numeric not null default 1,
	completion numeric not null default 0
);

create table if not exists task_dependencies(
	task_id INTEGER references tasks(name),
	prereq_id INTEGER references tasks(name)
);