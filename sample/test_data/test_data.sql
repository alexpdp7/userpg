insert into task_status(id) values ('todo');
insert into task_status(id) values ('doing');
insert into task_status(id) values ('done');

insert into
    tasks(id, title, description, due_date, status_id)
values
    ('CONQ', 'Conquer the world', 'Like every night', '2021-12-03 18:00', 'todo'),
    ('BRAIN', 'Grow a brain', 'Better than the last one', null, 'doing'),
    ('NICE', 'Be nicer to people', 'Why not?', null, 'done');

insert into
    task_dependencies (blocking_task_id, blocked_task_id)
values
    ('BRAIN', 'CONQ');
