#!/usr/bin/env python3
"""
api_openai.py – FastAPI backend (OpenAI edition)

• Unified /qa endpoint:
    - Intent classifier prompt decides SQL vs RAG
    - SQL path: LangChain SQLDatabaseChain
    - RAG path: PGVector + RetrievalQA with numeric-precision prompt

Env vars:
    OPENAI_API_KEY  – required
"""

from pathlib import Path
from functools import lru_cache

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ── LangChain core imports ────────────────────────────────────────────
from langchain_openai            import ChatOpenAI          # ← OpenAI LLM
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_community.utilities   import SQLDatabase
from langchain_experimental.sql      import SQLDatabaseChain
from langchain.chains                import RetrievalQA, LLMChain
from langchain.prompts               import PromptTemplate

# ── Configuration ─────────────────────────────────────────────────────
PG_URI         = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
VEC_COLLECTION = "energy_nodes"
SQL_TABLE      = "energy_merged"
EMBED_MODEL    = "all-MiniLM-L6-v2"
BASE           = Path(__file__).parent

print(">>> api_openai.py loading …")

# ── FastAPI app ────────────────────────────────────────────────────────
app = FastAPI(title="Energy QA API (OpenAI)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Embeddings + PGVector ─────────────────────────────────────────────
embedder = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)
vector_store = PGVector(
    connection_string = PG_URI,
    collection_name   = VEC_COLLECTION,
    embedding_function= embedder,
)

# ── OpenAI LLM (gpt-3.5-turbo-0125 • 16k ctx) ─────────────────────────
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2)

# ── RAG prompt (numeric precision) ────────────────────────────────────
NUMERIC_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Answer the QUESTION using only the numbers in CONTEXT. "
        "Compute ratios if needed (2 decimals). "
        "Return exactly ONE sentence.\n\n"
        "CONTEXT:\n{context}\n\nQUESTION: {question}\nANSWER:"
    ),
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": NUMERIC_PROMPT, "stop": ["\n"]},
    return_source_documents=False,
)

# ── SQL chain (schema-only prompt) ─────────────────────────────────────
sql_db = SQLDatabase.from_uri(
    PG_URI,
    include_tables=[SQL_TABLE],
)
schema_only = sql_db.get_table_info(table_names=[SQL_TABLE], num_rows=0)
sql_db._table_info = schema_only

sql_chain = SQLDatabaseChain.from_llm(llm, sql_db, verbose=False)

# ── Intent classifier prompt ──────────────────────────────────────────
INTENT_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=(
        "Respond with one word (SQL or RAG) indicating how to answer.\n"
        "\n"
        "Examples:\n"
        "Q: List all buildings that used more than 5000 kWh in June 2023\n"
        "→ SQL\n"
        "Q: Which district had the highest per-capita energy usage in July 2023?\n"
        "→ RAG\n"
        "\n"
        "User question: {question}\n"
        "→"
    ),
)

@lru_cache
def get_intent_chain():
    return LLMChain(llm=llm, prompt=INTENT_PROMPT, output_key="label")

# ── Unified /qa route ─────────────────────────────────────────────────
@app.get("/qa", summary="Ask anything (auto SQL or RAG)")
def unified_qa(q: str = Query(..., description="Your question")):
    label = get_intent_chain().run(question=q).strip().upper()
    print(f"[INTENT] {q!r}  → {label}")
    if label == "SQL":
        answer = sql_chain.run(q)
    else:
        answer = qa_chain.run(q)
    return {"answer": answer}

# ── Run standalone ────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("api_openai:app", host="0.0.0.0", port=8000, reload=True)

print(">>> api_openai.py imported OK")
