#!/usr/bin/env python3
# index.py — ingest into PGVector

import json
from pathlib import Path
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import PGVector

def main():
    BASE      = Path(__file__).parent
    docs_file = BASE / "docs.jsonl"

    # 1) Read all serialized node-documents
    texts, metas = [], []
    with open(docs_file, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texts.append(obj["text"])
            metas.append(obj["metadata"])

    # 2) Configure PGVector connection & collection name
    PG_URI = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
    COLLECTION = "energy_nodes"

    # 3) Embed & upsert into Postgres
    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    store = PGVector.from_texts(
        texts=texts,
        embedding=embedder,
        connection_string=PG_URI,
        collection_name=COLLECTION
    )

    print(f"✅ PGVector collection '{COLLECTION}' created with {len(texts)} vectors.")

if __name__ == "__main__":
    main()
