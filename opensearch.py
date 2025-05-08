
import boto3
import yaml
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

# boto_session = boto3.Session()
# region_name = boto_session.region_name
# INDEX_NAME = "example_queries"

def load_opensearch_config():
    with open("./libs/opensearch.yml", 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def init_opensearch(config):
    mapping = {"settings": config['settings'], "mappings": config['mappings-sql']}
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region_name, 'aoss')
    
    host = collection_endpoint.replace("https://", "").split(':')[0]
    
    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )
    create_os_index(client, mapping)
    return client

def create_os_index(client, mapping):
    exists = client.indices.exists(INDEX_NAME)
    if exists:
        client.indices.delete(index=INDEX_NAME)
        print("Existing index has been deleted. Create new one.")
    else:
        print("Index does not exist, Create one.")

    client.indices.create(INDEX_NAME, body=mapping)

#test
# config = load_opensearch_config()
# os_client = init_opensearch(config)


     
# We will convert the previously created natural language question & SQL query pairs into vector embeddings, and format them into a Data-Action format suitable for bulk indexing in OpenSearch.


import os

# FILE_PATH_2 = '../db_metadata/example_queries.jsonl'
# embed_model = "amazon.titan-embed-text-v2:0"

def input_embedding():
    num = 0
    if os.path.exists(FILE_PATH_2):
        os.remove(FILE_PATH_2)

    with open(FILE_PATH_1, 'r') as input_file, open(FILE_PATH_2, 'a') as output_file:
        for line in input_file:
            
            data = json.loads(line)
            input = data['input']
            query = data['query']

            response = boto3_client.invoke_model(
                modelId=embed_model,
                body=json.dumps({"inputText": input})
            )

            # Data part
            body = { "input": input, "query": query, "input_v": json.loads(response['body'].read())['embedding'] }

            # Action part
            action = { "index": { "_index": INDEX_NAME } }

            # Write action and body to the file in correct bulk format
            output_file.write(json.dumps(action, ensure_ascii=False) + "\n")
            output_file.write(json.dumps(body, ensure_ascii=False) + "\n")

            num += 1    

# input_embedding()


     
# In the db_metadata/example_queries.jsonl file, you can see the converted embeddings.

#test
# with open(FILE_PATH_2, 'r') as file:
#     bulk_data = file.read()
        
# response = os_client.bulk(body=bulk_data)
# if response["errors"]:
#     print("There were errors during bulk indexing:")
#     for item in response["items"]:
#         if 'index' in item and item['index']['status'] >= 400:
#             print(f"Error: {item['index']['error']['reason']}")
# else:
#     print("Bulk-inserted all items successfully.")