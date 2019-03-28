-- run pai to get pagerank result
drop table if exists dwd_pagerank;

PAI -name PageRankWithWeight
    -project algo_public
    -DinputEdgeTableName=ods_raw_pagerank
    -DfromVertexCol=from_user
    -DtoVertexCol=to_user
    -DoutputTableName=dwd_pagerank
    -DhasEdgeWeight=true
    -DedgeWeightCol=weight
    -DmaxIter 100;


-- add time information to sync out
drop table if exists dwd_pagerank_out;

create table if not exists dwd_pagerank_out (
    user string,
    weight double,
    ds string
);

insert into dwd_pagerank_out (user, weight, ds) select *, getdate() from dwd_pagerank;
