import json
import boto3
from botocore.vendored import requests
import time
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

lex_client = boto3.client('lex-runtime')

credentials = boto3.Session().get_credentials()
region = 'us-east-1'
service = 'es'
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def lambda_handler(event, context):
    # Get Keyword from Lex________________________________________________________________________
    print("DEBUG: event:", event)
    user_message = event['queryStringParameters']['q']

    if user_message == None:
        return{
            'statusCode': 200,
            'headers': { 
                'Access-Control-Allow-Headers' : 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body':json.dumps("No Message!")
        }
    
    response = lex_client.post_text(
        botName ='chatBotTwo',
        botAlias ='chatBotTwoAlias',
        userId = event['requestContext']['accountId'],
        inputText = user_message
    )
    print("DEBUG: response:", response)
    returnlist = []
    response_message = response['message']
    keywords = ['dog','cat','human','person','horse','fish','city','car','bus','elephant','bird','park','tree','building','truck','bear',\
    'flower','plant','computer','water','fire','monkey','smile','angry','face','shirt','clothing','apparel']
    
    for keyword in keywords:
        if keyword in response_message:
            returnlist.append(keyword)

    print("DEBUG: return list:", returnlist)
    
    #Look for elastic search and return list. FETCH the key__________________________
    es_endpoint = 'search-photos-jsltvsfmvvax7uaa4vw2zzp7ii.us-east-1.es.amazonaws.com'
    es = Elasticsearch(
        hosts = [{'host': es_endpoint, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    return_ids = es.search(index = "images", body = {
        "query":{
            'terms':{
                'labels': returnlist
            }}})
    
    print("DEBUG: return ids", return_ids)
    tempp = return_ids['hits']['hits']
    print("DEBUG: tempp", tempp)

    
    returnid = []
    for temp in tempp:
        print("DEBUG: temp source objectkey", temp['_source']['ObjectKey'])
        returnid.append("URL__________/"+str(temp['_source']['ObjectKey']))
    print("DEBUG: return list", returnlist)
    print("DEBUG: return id", returnid)
    returnvals = {
        'keywords': returnlist,
        'ids': returnid
    }
    
    return {
        'statusCode': 200,
        'headers': { 
            'Access-Control-Allow-Headers' : 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': returnvals
    }