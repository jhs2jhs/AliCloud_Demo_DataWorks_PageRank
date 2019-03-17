create table if not exists dwd_pagerank (
    user string,
    weight double
) 
partitioned by (ds string);
