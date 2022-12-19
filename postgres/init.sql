create table if not exists users(
    id bigint generated always as identity,
    real_name varchar,
    primary key(id)
);

create table if not exists telegrams(
    user_id bigint references users(id),
    telegram_name varchar,
    telegram_nickname varchar,
    telegram_id varchar
);

create table if not exists wireguard_client_confs(
    id bigint generated always as identity,
    user_id bigint references users(id),
    ip cidr,
    ip_mask int,
    dns cidr,
    private_key char(44),
    public_key char(44),
    primary key (id)
);

create table if not exists stat_logs(
    conf_id bigint references wireguard_client_confs(id),
    log_time timestamp not null default now(),
    last_handshake timestamp,
    transfer_rx bigint,
    transfer_tx bigint
);

create table if not exists conf_stats(
    conf_id bigint references wireguard_client_confs(id),
    stat int,
    time timestamp not null default now()

);


