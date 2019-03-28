# AliCloud Demo of Dataworks for PageRank

# Purpose
It demonstrates on a use case to integrate Dataworks with API call, including:
1. create a PageRank algorithm in PAI
2. create data ingestion and sync in DataWorks
3. create step 1 and step 2 into a worktask and call externally in API
4. create a wrapper around API call to extend the integration

# Value 
It demonstrates one of several ways to use Alibaba Cloud as part of a e2e BigData/MachineLearning service.

# Workshop Step-by-Step

## upload data into oss
create a new oss bucket called “demopageranker”. 
![alt](/demo_screenshot/oss_create.png)
Create a ‘in’ folder to keep raw input data, and a ‘out’ folder for result.
![alt](/demo_screenshot/oss_create_folder_layout.png)
Change filename locally into “slack_example_with_head.csv” [or any other file name you like]. Click on “upload” button to upload the file. 
![alt](/demo_screenshot/oss_upload.png)
Note down endpoint connection configuration information. 
![alt](/demo_screenshot/oss_access.png)

## create dataworks workflow
go to datawork [console](https://workbench.data.aliyun.com/consolenew#/) and create a workspace if you have not. For example, I created workspace called “jhs_pagerank_sh”. Make sure you select to enable PAI and Data Integration. 
![alt](/demo_screenshot/dw_create_workspace.png)

Click on “data integration” button in the workspace and then connect dataworks to oss:
![alt](/demo_screenshot/dw_connect_data_source.png)
![alt](/demo_screenshot/dw_connect_data_source_oss.png)
![alt](/demo_screenshot/dw_oss_connect_test.png)

The AccessKey info can be found in : https://usercenter.console.aliyun.com/#/manage/ak 
![alt](/demo_screenshot/dw_get_ak.png)

Go to “datastudio” in dataworks and then select __Ad-hoc business flow__ to create a ad-hoc business flow, such as “pagerank_sh_adhoc”. At the moment, only __Ad-hoc business flow__ can work with API, others can only work with schedule in IDE. 
![alt](/demo_screenshot/dw_create_adhoc_bf.png)

In the business flow, let us design a workflow as bellow:
![alt](/demo_screenshot/dw_wf_overview.png)

“vn_start” is a virtual node. Make sure you configure to use root node as bellow:
![alt](/demo_screenshot/dw_virtual_node.png)

in “ddl_ods_pagerank”, copy paste bellow sql, and then click on “save” button and then click on “run” button. This SQL will ignore partition setting since we only have a very small SQL. This step will create a table called “ods_raw_pagerank” to store data ingested from oss. [SQL](/sql_ddl_ods_pagerank.sql)

```
create table if not exists ods_raw_pagerank (
    from_user string,
    to_user string,
    weight double
);
```



.png

.png
.png



![alt](/demo_screenshot/dw_create_workspace.png)


curl http://demopageranker.oss-eu-central-1.aliyuncs.com/dwd_pagerank_out.csv
