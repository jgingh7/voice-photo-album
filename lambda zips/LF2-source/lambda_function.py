import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

lex_client = boto3.client('lex-runtime')

credentials = boto3.Session().get_credentials()
region = 'us-east-1'
service = 'es'
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def lambda_handler(event, context):
    
    # --------------------------------- get keyword form Lex ---------------------------------
    
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
    
    if response['dialogState'] == 'ElicitIntent':
        return {
            'statusCode': 200,
            'headers': { 
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps({
                "results": {
                    'keywords': [],
                    'ids': []
                }
            })
        }
    
    returnlist = [response['slots']['imageA']]
    if response['slots']['imageB']:
        returnlist.append(response['slots']['imageB'])
    if response['slots']['imageC']:
        returnlist.append(response['slots']['imageC'])
    if response['slots']['imageD']:
        returnlist.append(response['slots']['imageD'])
    if response['slots']['imageE']:
        returnlist.append(response['slots']['imageE'])

    
    print("DEBUG: return list:", returnlist)
    
    
    # --------------------------------- Look for elastic search and return list ---------------------------------
    
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
    temps = return_ids['hits']['hits']
    print("DEBUG: temps", temps)

    
    returnid = []
    bucket = "photophotobucket"
    for temp in temps:
        print("DEBUG: temp source objectkey", temp['_source']['ObjectKey']) #me.png #jin-profile.png
        returnid.append(f"https://{bucket}.s3.amazonaws.com/{str(temp['_source']['ObjectKey'])}")
    print("DEBUG: return id", returnid)
    returnvals = {
        'keywords': returnlist,
        'ids': returnid
    }
    
    return {
        'statusCode': 200,
        'headers': { 
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps({
            "results": returnvals
        })
    }
    
# THE RETURNED VALUE
#     {
#     "results": {
#         "keywords": [
#             "human"
#         ],
#         "ids": [
#             "https://photophotobucket.s3.amazonaws.com/me.png",
#             "https://photophotobucket.s3.amazonaws.com/jin-profile.png"
#         ]
#     }
# }