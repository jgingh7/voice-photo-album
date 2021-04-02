import json
import boto3
from botocore.vendored import requests
import time
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


rek_client = boto3.client('rekognition')


def lambda_handler(event, context):
    
    # Use rekognition to detect labels
    print("CODE TESTER")
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    
    pass_object = {
        'S3Object': {
            'Bucket':bucket_name,
            'Name':key_name
            }
        }
    response = rek_client.detect_labels(Image=pass_object, MaxLabels=10, MinConfidence=75)

    timestamp = time.time()
    labels = []
    for i in range(len(response['Labels'])):
        labels.append(response['Labels'][i]['Name'])
    
    
    print("DEBUG: LABELS:", labels)
    # Upload data to Elastic Search 
    document = {
        'ObjectKey':key_name,
        'Bucket':bucket_name,
        'timestamp':timestamp,
        'labels':labels
    }
    
    print("DEBUG:", format)
    host = 'URL' # For example, my-test-domain.us-east-1.es.amazonaws.com
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
    
    
    es.index(index="images", doc_type="_doc", id=key_name, body=document)
    
    print(es.get(index="images", doc_type="_doc", id=key_name))
    
    
    
    

# import logging
# from aws_requests_auth.aws_auth import AWSRequestsAuth

# logger = logging.getLogger()
# es_host = os.getenv('ELASTICSEARCH_URL')
# es_index = 'images'
# access_key = os.getenv('AWS_ACCESS_KEY_ID')
# secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# session_token = os.getenv('AWS_SESSION_TOKEN')
# region = os.getenv('AWS_REGION')

# # Create clients for AWS services
# rek_client = boto3.client('rekognition')

# # Establish connection to ElasticSearch
# auth = AWSRequestsAuth(aws_access_key=access_key,
#                       aws_secret_access_key=secret_access_key,
#                       aws_token=session_token,
#                       aws_host=es_host,
#                       aws_region=region,
#                       aws_service='es')

# es = Elasticsearch(host=es_host,
#                   port=443,
#                   use_ssl=True,
#                   connection_class=RequestsHttpConnection,
#                   http_auth=auth)

# logger.info("{}".format(es.info()))


# def lambda_handler(event, context):
#     """Lambda Function entrypoint handler
#     :event: S3 Put event
#     :context: Lambda context
#     :returns: Number of records processed
#     """
#     processed = 0
#     for record in event['Records']:
#         s3_record = record['s3']

#         key = s3_record['object']['key']
#         bucket = s3_record['bucket']['name']
        
#         resp = rek_client.detect_labels(
#             Image={'S3Object': {'Bucket': bucket, 'Name': key}},
#             MaxLabels=10,
#             MinConfidence=80)
            
#         labels = []
#         for l in resp['Labels']:
#             labels.append(l['Name'])
        
#         logger.debug('Detected labels: {}'.format(labels))
#         res = es.index(index=es_index, doc_type='event',
#                       id=key, body={'labels': labels})

#         logger.debug(res)
#         processed = processed + 1

#     logger.info('Successfully processed {} records'.format(processed))
#     return processed