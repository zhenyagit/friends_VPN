create table if not exists users(
    id bigint generated always as identity,
    ip cidr,
    real_name varchar,
    private_key char(44),
    public_key char(44),
    primary key(id)
);

create table if not exists telegrams(
    user_id bigint references users(id),
    telegram_name varchar,
    telegram_id varchar
);

create table if not exists stat_logs(
    id bigint generated always as identity,
    user_id int references users(id),
--     log_time timestamp,
    log_time timestamp not null default now(),
    last_handshake timestamp,
    transfer_rx bigint,
    transfer_tx bigint,
    primary key (id)
);

create table if not exists user_statuses(
    user_id int references users(id),
    status int
);


