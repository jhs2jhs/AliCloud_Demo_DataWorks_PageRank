create table if not exists ods_pagerank (
    from_user string,
    to_user string,
    weight double
) 
partitioned by (ds string);
