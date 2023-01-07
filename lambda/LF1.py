# reference:
# https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html
# https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html#detectlabels-response
import json
import boto3
import urllib.parse
from opensearchpy import OpenSearch, RequestsHttpConnection,AWSV4SignerAuth

region = 'us-east-1'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region)

host = 'search-photos-ynhsoyixzu3m5nem64i4npt4sm.us-east-1.es.amazonaws.com'
index = 'photos'


rekClient = boto3.client('rekognition')
s3Client = boto3.client('s3')

def get_metadata(photo, bucket):
    try:
        response = s3Client.head_object(Bucket=bucket, Key=photo)
        print(response)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    label_arr = []
    if 'customlabels' in response['Metadata']:
        label_raw = response['Metadata']['customlabels']
        label_arr = label_raw.split(", ")
        for i in range(len(label_arr)):
            label_arr[i] = label_arr[i].lower()
    return label_arr

def detect_labels(photo, bucket, label_arr):
    response = rekClient.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)

    print('Detected labels for ' + photo)
    
    for label in response['Labels']:
        if label['Name'] not in label_arr:
            label_arr.append(label['Name'].lower())

    return len(response['Labels']), label_arr


def lambda_handler(event, context):
    print('LF1 invoked by S3!')
    print("Received event: " + json.dumps(event))
    if event['Records'][0]["eventName"] != "ObjectCreated:Put":
        return {
            'statusCode': 200,
            'body': json.dumps('LF1 invoked by S3, but nothing happened!')
        }
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    seq = event['Records'][0]['s3']['object']['sequencer']
    timestamp = event['Records'][0]['eventTime']
    label_arr = get_metadata(key, bucket)
    label_count, label_arr = detect_labels(key, bucket, label_arr)
    print("Current Labels: ", label_arr)
    img_object = {}
    img_object["objectKey"] = key
    img_object["bucket"] = bucket
    img_object["createdTimestamp"] = timestamp
    img_object["labels"] = label_arr
    
    img_object = json.dumps(img_object)
    print(img_object)
    
    es = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        use_ssl=True,
        verify_certs=True,
        http_auth=auth,
        connection_class=RequestsHttpConnection
    )
    
    resp = es.index(index="photos", id=seq, body=img_object)
    print("resp from es: ", resp)
    

    return {
        'statusCode': 200,
        'body': json.dumps('LF1 invoked by S3!')
    }