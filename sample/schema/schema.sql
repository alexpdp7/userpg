create table task_status (
    id                       text primary key
);

create table tasks (
    id                       text primary key,
    title                    text not null,
    description              text,
    due_date                 timestamp with time zone null,
    status_id                text not null references task_status(id) deferrable
);

create table task_dependencies (
    blocking_task_id         text not null references tasks(id) deferrable,
    blocked_task_id          text not null references tasks(id) deferrable,
    primary key(blocking_task_id, blocked_task_id)
);
