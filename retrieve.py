import json

embed_model = "amazon.titan-embed-text-v2:0"

def input_embedding(example):
    for example in examples:
        input_text = example['input']
        query = example['query']

        response = boto3_client.invoke_model(
            modelId=embed_model,
            body=json.dumps({"inputText": input_text})
        )

        # Data part
        body = {
            "input": input_text,
            "query": query,
            "input_v": json.loads(response['body'].read())['embedding']
        }
        memory_storage.append(body)

from scipy.spatial.distance import cosine
import heapq

def find_most_similar_samples(question_v, memory_storage, top_k=3):
    similar_docs = []

    for doc in memory_storage:
        # Cosine similarity 
        similarity = 1 - cosine(question_v, doc['input_v'])

        if len(similar_docs) < top_k:
            heapq.heappush(similar_docs, (similarity, doc))
        elif similarity > similar_docs[0][0]:
            heapq.heapreplace(similar_docs, (similarity, doc))


    return sorted(similar_docs, key=lambda x: x[0], reverse=True)
