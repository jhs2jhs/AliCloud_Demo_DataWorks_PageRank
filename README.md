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

## create dataworks task
go to datawork [console](https://workbench.data.aliyun.com/consolenew#/) and create a workspace if you have not. For example, I created workspace called “jhs_pagerank_sh”. Make sure you select to enable PAI and Data Integration. 
![alt](/demo_screenshot/dw_create_workspace.png)

Click on “data integration” button in the workspace and then connect dataworks to oss:
![alt](/demo_screenshot/dw_connect_data_source.png)
![alt](/demo_screenshot/dw_connect_data_source_oss.png)
![alt](/demo_screenshot/dw_oss_connect_test.png)

The AccessKey info can be found in : https://usercenter.console.aliyun.com/#/manage/ak 
![alt](/demo_screenshot/dw_get_ak.png)

Go to “datastudio” in dataworks to create a business flow, such as “pagerank_sh_adhoc”

.png

.png
.png



![alt](/demo_screenshot/dw_create_workspace.png)


curl http://demopageranker.oss-eu-central-1.aliyuncs.com/dwd_pagerank_out.csv
