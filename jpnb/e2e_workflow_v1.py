#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
#coding=utf-8


# In[2]:


import config

accesskey_id = config.alicloud_accesskey_id
accesskey_secret = config.alicloud_accesskey_secret
region_id = config.alicloud_region_id

projectname = config.alicloud_dataworks_projectname
flowname = config.alicloud_dataworks_flowname
bizdate = config.alicloud_dataworks_bizdate
bizdate = config.alicloud_dataworks_bizdate

oss_bucket = config.alicloud_oss_bucket
oss_endpoint = config.alicloud_oss_endpoint

http_root = 'http://%s.%s/'%(oss_bucket, oss_endpoint)
print(http_root)


# # Preparation 1: function for oss

# In[3]:


import oss2 # pip install oss2
import os
import datetime

def oss_check_fn(prefix):
    result = bucket.list_objects(prefix=prefix, delimiter='', marker='', max_keys=100)
    fn = ''
    ts = ''
    for r in result.object_list:
        #print(r.key)
        if ts == '':
            ts = r.last_modified
        if ts >= r.last_modified:
            ts = r.last_modified
            fn = r.key
            bucket.put_object_acl(fn, oss2.BUCKET_ACL_PUBLIC_READ)
            
    return fn

def oss_validate_fn(key):
    result = bucket.get_object(key)
    
    with open(key, "rb") as binary_file:
        # Read the whole file at once
        content = binary_file.read()

    content_got = b''
    for chunk in result:
        content_got += chunk
    assert content_got == content
    
    filename = 'download.txt'
    result = bucket.get_object_to_file(key, filename)
    
    with open(filename, 'rb') as fileobj:
        assert fileobj.read() == content
        

def oss_upload_fn(key):
    with open(key, "rb") as binary_file:
        # Read the whole file at once
        content = binary_file.read()
    bucket.put_object(key, content, headers={})
    bucket.put_object_acl(key, oss2.BUCKET_ACL_PUBLIC_READ)
    

def oss_check_out_fn(prefix):
    fn = '%s%s'%(http_root, oss_check_fn(prefix))
    return fn


# In[4]:


# Preparation 2: function for dataworks


# In[5]:


import json
from pprint import pprint
import datetime
import time

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

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


# # Step 1: upload a source CSV from local to oss

# In[6]:


bucket = oss2.Bucket(oss2.Auth(accesskey_id, accesskey_secret), oss_endpoint, oss_bucket)
print(bucket)

key = 'in/slack_example_with_head.csv'
oss_upload_fn(key)

fn = '%s%s'%(http_root, oss_check_fn(key))
print(fn)

oss_validate_fn(key)

import requests
r = requests.get(fn)
print(r.text)


# # Step 2: create DAG and wait it for finish in dataworks

# In[7]:


js, status, dag_id = dataworks_api_create_adhoc_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, bizdate)

print('api_return: ')
pprint(js)
print('status: ',  status)
print('dag_id: ', dag_id)


# In[8]:


js, status = dataworks_api_check_dag(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id)

print('api_return: ')
pprint(js)


# In[9]:


wait_for_dag_to_complete(accesskey_id, accesskey_secret, region_id, projectname, flowname, dag_id)


# # Step 3: get output file address to curl

# In[10]:


bucket = oss2.Bucket(oss2.Auth(accesskey_id, accesskey_secret), oss_endpoint, oss_bucket)
print(bucket)

prefix='out/dwd_'
fn = oss_check_out_fn(prefix)
print(fn)

import requests
r = requests.get(fn)
print(r.text)


# In[ ]:




