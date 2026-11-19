create table if not exists tasks(
	id INTEGER primary key,
	parent_id INTEGER references tasks(id),
	title TEXT UNIQUE not null,
	weight numeric not null default 1,
	completion numeric not null default 0
);

create table if not exists task_dependencies(
	task_id INTEGER references tasks(id),
	prereq_id INTEGER references tasks(id),
);