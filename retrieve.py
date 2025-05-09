import json
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

def chunk_txt_by_line(file_path, max_lines=100):
    chunks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            # if i >= max_lines:
            #     br
            #     eak
            line = line.strip()
            if line:  # 빈 줄은 제외 (필요 없으면 이 줄 삭제 가능)
                chunks.append(line)
    return chunks

file_path = '/content/drive/MyDrive/ninewatt/mart_djy_03_daegu.txt'
chunks = chunk_txt_by_line(file_path)


documents = [Document(page_content=text,metadata = {'source':'/content/drive/MyDrive/ninewatt/mart_djy_03_daegu.txt'})
for text in chunks]

index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)
uuids = [str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)

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
