import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection,AWSV4SignerAuth
from datetime import datetime
import inflect

p = inflect.engine()

region = 'us-east-1'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region)
s3_url = 'https://6998-hw2-b2.s3.amazonaws.com/'

host = 'search-photos-ynhsoyixzu3m5nem64i4npt4sm.us-east-1.es.amazonaws.com'
index = 'photos'
es = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

lex_client = boto3.client('lexv2-runtime')

def search_es(msg):
    headers = {"Content-Type":"application/json"}
    
    es_query = {
        "size": 100,
        "query": {
            "query_string": {
                "default_field": "labels",
                "query": msg
            }
        }
    }
    r = es.search(body = es_query, index = "photos")
    resp = r['hits']['hits']
    return resp

def extract_photos(keywords):
    print(keywords)
    if len(keywords) == 0:
        return []
    photo_set1 = set()
    search_rst1 = search_es(keywords[0])
    for photo_object in search_rst1:
        photo_name = photo_object["_source"]["objectKey"]
        photo_set1.add(photo_name)
    if len(photo_set1) == 0:
        singular_key1 = p.singular_noun(keywords[0])
        search_rst1 = search_es(singular_key1)
        for photo_object in search_rst1:
            photo_name = photo_object["_source"]["objectKey"]
            photo_set1.add(photo_name)

    if(len(keywords) == 1):
        return list(photo_set1)

    photo_set2 = set()
    search_rst2 = search_es(keywords[1])
    for photo_object in search_rst2:
        photo_name = photo_object["_source"]["objectKey"]
        photo_set2.add(photo_name)
    if len(photo_set2) == 0:
        singular_key2 = p.singular_noun(keywords[1])
        search_rst2 = search_es(singular_key2)
        for photo_object in search_rst2:
            photo_name = photo_object["_source"]["objectKey"]
            photo_set2.add(photo_name)

    photo_fin_set = photo_set1.union(photo_set2)
    return list(photo_fin_set)
    
def lambda_handler(event, context):
    # TODO implement
    print("event: ",event)
    print("context: ",context)
    msg_from_user = event["q"]
    # Initiate conversation with Lex
    response = lex_client.recognize_text(
            botId='WIOWP3EEDF', # MODIFY HERE
            botAliasId='TSTALIASID', # MODIFY HERE
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user)
    
    msg_from_lex = response.get('messages', [])
    # request_id = response.get('ResponseMetadata',[])
    
    session_state = response.get("sessionState", [])
    keywords_slots = session_state["intent"]["slots"]
    keywords = []
    for kw in keywords_slots:
        if keywords_slots[kw]:
            keywords.append(keywords_slots[kw]["value"]["interpretedValue"])

        
    print("filter result:")  
    search_labels = extract_photos(keywords)
    print(search_labels)
    search_urls = []
    for lab in search_labels:
        search_urls.append(s3_url+lab)
    
    msgs = []
    if msg_from_lex:
        current_day = datetime.now()
        for idx in range(len(msg_from_lex)):
            unit_msg = msg_from_lex[idx]
            print(f"Message from Chatbot: {unit_msg['content']}")
            single_msg = {
                'type':'array',
                'array':{
                    'url': '',
                    'labels': search_urls
                }
            }
            msgs.append(single_msg)
        print(response)
        
    resp = {
        'statusCode': 200,
        'body': "Hello from LF2!",
        'messages': msgs
    }

    return resp
