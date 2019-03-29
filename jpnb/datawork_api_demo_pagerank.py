#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
#coding=utf-8

import json
from pprint import pprint
import datetime
import time


# In[2]:


from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


# In[3]:


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
    


# In[4]:


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


# # Config # AK is better to be managed in a seperate file

# In[5]:


accesskey_id = 'xxx' # from your alibaba cloud account
accesskey_secret = 'xxx' # from your alibaba cloud account
region_id = 'cn-shanghai'

projectname = 'jhs_pagerank_sh'
flowname = 'pagerank_sh_adhoc'
bizdate = str(datetime.datetime.now()).split('.')[0]
bizdate = '2019-03-28 00:00:00'


# # get dag api

# In[6]:


js, status, dag_id = dataworks_api_create_adhoc_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, bizdate)

print('api_return: ')
pprint(js)
print('status: ',  status)
print('dag_id: ', dag_id)


# # start to get status of api

# In[7]:


js, status = dataworks_api_check_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id)


# In[8]:


print('api_return: ')
pprint(js)


# In[ ]:


def check_dag_status(status_code):
    dag_status = {
        1: {'en': 'NOT_RUN', 'cn': "未运行"},
        2: {'en': 'WAIT_TIME', 'cn': "等待时间"},
        3: {'en': 'WAIT_RESOURCE', 'cn': "等待资源"},
        4: {'en': 'RUNNING', 'cn': "运行中"},
        5: {'en': 'FAILURE', 'cn': "运行失败"},
        6: {'en': 'SUCCESS', 'cn': "运行成功"},
        7: {'en': 'CHECKING', 'cn': "校验中"}
    }
    if status_code in dag_status:
        return dag_status[status_code]
    else:
        return 'invalidate status_code, please check'
    
def dt_to_ds(dt):
    dt = int(dt)
    ds = datetime.datetime.fromtimestamp(dt / 1e3)
    return ds

def wait_for_dag_to_complete(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id):
    while True:
        js, status = dataworks_api_check_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id)
        dag_finish = 1
        if ('Data' in js) and ('NodeInsInfo' in js['Data']):
            for node in js['Data']['NodeInsInfo']:
                dag_id = node['DagId']
                biz_date = node['Bizdate']
                instance_id = node['InstanceId']
                create_time = node['CreateTime']
                modify_time = node['ModifyTime']
                status = check_dag_status(node['Status'])
                print('%s | %s | %s \n | %s | %s | %s'%(dag_id, instance_id, status, dt_to_ds(biz_date), dt_to_ds(create_time), dt_to_ds(modify_time)))
                if node['Status'] != 6:
                    dag_finish = 0
        if dag_finish == 1:
            print("** whole dag is completed, please go to oss to fetch latest file **")
            break
        else:
            print("**** please wait for the dag to be complete.... ****")
            time.sleep(5)

            #js, status = dataworks_api_check_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, instance_id)
            #pprint(js)
    return 

wait_for_dag_to_complete(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id)
    


# In[ ]:


# TODO: further work to check on status and decide if to run in the future


# In[ ]:




