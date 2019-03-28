create table if not exists ods_raw_pagerank (
    from_user string,
    to_user string,
    weight double
);

-- attention, we ignore partition for this demo
