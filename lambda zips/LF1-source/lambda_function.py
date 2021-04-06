import json
import boto3
from botocore.vendored import requests
import time
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


rek_client = boto3.client('rekognition')
s3_client = boto3.client('s3')

credentials = boto3.Session().get_credentials()
region = 'us-east-1'
service = 'es'
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


def lambda_handler(event, context):
    
    # Use rekognition to detect labels
    print("DEBUG: event:", event)
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name'] #photophotobucket
    key_name = s3_info['object']['key'] #jin-profile.png
    

    s3_response = s3_client.head_object(
        Bucket = bucket_name,
        Key = key_name
    )
    print('DEBUG: s3_response:', s3_response)
    custom_label = s3_response['Metadata']['customlabels']
    custom_label_list = custom_label.split(",")
    custom_label_list = map(lambda x: x.strip(), custom_label_list)

    
    pass_object = {
        'S3Object': {
            'Bucket':bucket_name,
            'Name':key_name
            }
        }
    response = rek_client.detect_labels(Image = pass_object, MaxLabels = 10, MinConfidence = 75)
    
    print("DEBUG: response:", response)
    
    timestamp = time.time()
    labels = []
    for i in range(len(response['Labels'])):
        labels.append(response['Labels'][i]['Name'])
    labels += custom_label_list
    
    
    # LABELS: ['Face', 'Person', 'Human', 'Hair', 'Shirt', 'Clothing', 'Apparel']
    print("DEBUG: LABELS:", labels)
    
    # Upload data to Elastic Search 
    document = {
        'ObjectKey': key_name,
        'Bucket': bucket_name,
        'timestamp': timestamp,
        'labels': labels
    }
    
    es_endpoint = 'search-photos-jsltvsfmvvax7uaa4vw2zzp7ii.us-east-1.es.amazonaws.com'
    es = Elasticsearch(
        hosts = [{'host': es_endpoint, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    es.index(index = "images", doc_type = "_doc", id = key_name, body = json.dumps(document))
    
    print("DEBUG: es.get:", es.get(index = "images", doc_type = "_doc", id = key_name))