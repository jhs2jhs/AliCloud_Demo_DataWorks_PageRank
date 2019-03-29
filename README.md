# AliCloud Demo of Dataworks for PageRank

# Purpose
It aims to demonstrate on how to integrate AlibabaCloud Dataworks product with API to other non-AlibabaCloud product. 
It demonstrate how to use Python or other SDK to control BigData/MachineLearning workflow in Dataworks which is supported by MaxComputer and PAI engine behind. It includes:
1. create a PageRank algorithm in PAI
2. create data ingestion and sync in DataWorks
3. create step 1 and step 2 into a worktask and call externally in API
4. create a python wrapper around API call to extend the integration

# Architecture

![alt](/demo_screenshot/demo_architecture.png)


# Value 
Alibaba CLoud BigData/MachineLearning products are often to be used standalone in its console. However, many cases that enterprise has its own control policy, e.g. CI/CD. Therefore, it is important to show how we can integrate Alibaba Cloud products with API call. 

# Product 

## Dataworks
Introduction and Documentation:
1. [English](https://www.alibabacloud.com/help/doc-detail/94780.htm)
2. [Chinese](https://help.aliyun.com/document_detail/93254.html)

## MaxCompute
[Introduction](https://www.alibabacloud.com/product/maxcompute)

## PAI
[Introduction](https://www.alibabacloud.com/product/machine-learning)


# Workshop Step-by-Step

## upload data into oss [this step can be replaced via API/SDK call to interact with OSS]
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
![alt](/demo_screenshot/dw_create_adhoc_bf.jpg)

In the business flow, let us design a workflow as bellow:
![alt](/demo_screenshot/dw_wf_overview.jpg)

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
![alt](/demo_screenshot/dw_ddl_ods.png)


In “sync_oss_to_odps”, we configure to set up data ingestion from oss and store in odps (MaxCompute). Click “run” button to do the first ingestion. 
![alt](/demo_screenshot/dw_sync_oss_to_odps.png)


In “ddl_dwd_pagerank”, paste bellow sql to create a placeholder to store result from PAI. The table is called “dwd_pagerank_out”.
```
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
```
![alt](/demo_screenshot/dw_ddl_dwd_pagerank.jpg)

Go back to dataworks, and do last step to sync data into oss for further consumption. And then run it. 
![alt](/demo_screenshot/dw_sync_opds_to_oss.png)

You can do back to the canvas. Run all process in one go. 
![alt](/demo_screenshot/dw_run_in_one_go.jpg)

You can see the result file appear in /out/ folder.
![alt](/demo_screenshot/oss_out.png)

You can test if output file can be visit with http get
![alt](/demo_screenshot/oss_out_check.png)


## publish datawork workflow so we can call in API
You need to submit the manual ad-hoc task in order to be called via api. 
![alt](/demo_screenshot/dw_submit.jpg)
![alt](/demo_screenshot/dw_submit_complete.jpg)

## configure python environment to call API
install [brew](https://brew.sh/) if you have not done so in macbook:
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

install [python3, pip3](https://docs.brew.sh/Homebrew-and-Python) if you have not done so in brew, it should also work in python2 and pip2
```
brew install python ## install python3.x
brew install python@2 ## install python2.x
pip2 --version
pip3 --version
```

install [jupyter notebook](https://jupyter.readthedocs.io/en/latest/install.html) if you have not done so in brew:
```
pip3 install --upgrade pip
pip3 install jupyter
```

install [aliyun-python-sdk](https://github.com/aliyun/aliyun-openapi-python-sdk)
```
# Install the core library
pip3 install aliyun-python-sdk-core
```

python function to create a manual dag instance
```
def dataworks_api_create_adhoc_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, bizdate='2018-07-25 00:00:00'):
    client = AcsClient(accesskey_id, accesskey_secret, region_id)

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dataworks.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https') # https | http
    request.set_version('2018-06-01')
    request.set_action_name('CreateManualDag')
    
    request.add_query_param('ProjectName', projectname)
    request.add_query_param('FlowName', flowname)
    request.add_query_param('Bizdate', bizdate)

    response = client.do_action(request)
    #pprint(response)
    js = json.loads(response)
    status = 'Failed and unknown'
    dag_id = '0'
    if ('ReturnCode' in js):
        if (js['ReturnCode'] == '600011'):
            status = 'Failed and Bizdate should be in [2019-03-20 00:00:00 format]'
        if (js['ReturnCode'] == '0') and ('ReturnValue' in js): 
            status = 'Succeed'
            dag_id = js['ReturnValue']
    return js, status, dag_id
    
```

python function to retrive dag runing status:
```
def dataworks_api_check_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id):
    client = AcsClient(accesskey_id, accesskey_secret, region_id)

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dataworks.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https') # https | http
    request.set_version('2018-06-01')
    request.set_action_name('SearchManualDagNodeInstance')

    request.add_query_param('ProjectName', projectname)
    request.add_query_param('DagId', dag_id)

    response = client.do_action(request)
    js = json.loads(response)
    status = 'Failed and unknown'
    if 'ErrCode' in js:
        if js['ErrCode'] == '11020293069':
            status = 'dag_id is not validated'
        if js['ErrCode'] == '0':
            status = 'Succeed'
    return js, status
```

a complete e2e run-through via jupyter notebook is provided: [jupyter notebook in python3](/jpnb/datawork_api_demo_pagerank.ipynb)



![alt](/demo_screenshot/dw_create_workspace.png)


curl http://demopageranker.oss-eu-central-1.aliyuncs.com/dwd_pagerank_out.csv
