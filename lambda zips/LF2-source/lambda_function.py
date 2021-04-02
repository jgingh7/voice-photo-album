import json
import boto3
from botocore.vendored import requests
import time
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

client = boto3.client('lex-runtime')


def lambda_handler(event, context):
    # Get Keyword from Lex________________________________________________________________________
    print(event)
    user_message = event['text']

    if user_message == None:
        return{
            'statusCode': 200,
            'body':json.dumps("No Message!")
        }
    
    response = client.post_text(
        botName='imagefind',
        botAlias='imagetexter',
        userId= 'userId',
        inputText= user_message
    )
    returnlist = []
    returnid=[]
    response2 = response['message']
    keywords = ['dog', 'cat', 'human', 'horse','fish','city','car','bus', 'elephant','bird','park','tree','building','truck','bear','flower','plant','computer','water','fire','monkey']
    
    for i in keywords:
        if i in response2:
            returnlist.append(i)

    print("DEBUG return list:", returnlist)
    
    #Look for elastic search and return list. FETCH the key__________________________
    host = 'URL__________' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-east-1' # e.g. us-west-1
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    return_ids = es.search(index="images", body={
    "query":{
        'terms':{
            'labels':returnlist
        }
    }
    })
    
    tempp=return_ids['hits']['hits']
    
    for temp in tempp:
        print(temp['_source']['ObjectKey'])
        returnid.append("URL__________/"+str(temp['_source']['ObjectKey']))
    print("DEBUG: return list", returnlist)
    print("DEBUG: return id", returnid)
    returnvals = {
        'keywords':returnlist,
        'ids':returnid
    }
    
    return {
        'statusCode': 200,
        'body': returnvals
    }