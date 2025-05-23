#!/usr/bin/env python3
"""
api.py  –  FastAPI backend (v3  -  fixed include_tables + SQL chain)
"""

from pathlib import Path
import re, uvicorn
from functools import lru_cache
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# ── LangChain
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_community.utilities   import SQLDatabase
from langchain_experimental.sql      import SQLDatabaseChain
from langchain.chains                import RetrievalQA, LLMChain
from langchain.prompts               import PromptTemplate

# ── LLM: local llama.cpp  (fallback → OpenAI if not installed)
try:
    from langchain_community.llms import LlamaCpp
    LOCAL_MODEL = True
except ImportError:
    from langchain_openai import ChatOpenAI
    LOCAL_MODEL = False

# ──────────────────────────  Config  ───────────────────────────
PG_URI         = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
SQL_TABLE      = "energy_merged"
SQL_VIEW       = "district_percapita"          # <- new
VEC_COLLECTION = "energy_nodes"
EMBED_MODEL    = "all-MiniLM-L6-v2"
MODEL_PATH     = Path(__file__).parent / "models" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# ──────────────────────────  FastAPI  ──────────────────────────
app = FastAPI(title="Energy RAG + SQL API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"],
)

# ─────────────────────  Embeddings & VectorStore  ──────────────
embedder = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)
vector_store = PGVector(
    connection_string = PG_URI,
    collection_name   = VEC_COLLECTION,
    embedding_function= embedder,
)

# ───────────────────────────  LLM  ────────────────────────────
if LOCAL_MODEL:
    llm = LlamaCpp(model_path=str(MODEL_PATH), n_ctx=2048,
                   n_threads=4, temperature=0.2, max_tokens=256)
else:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# ─────────────────────────  Graph-RAG  ─────────────────────────
NUMERIC_PROMPT = PromptTemplate(
    input_variables=["context","question"],
    template=(
        "Answer the QUESTION using only the numbers in CONTEXT. "
        "Compute ratios if needed (2 decimals). "
        "Return exactly ONE sentence.\n\n"
        "CONTEXT:\n{context}\n\nQUESTION: {question}\nANSWER:"
    ),
)
qa_chain = RetrievalQA.from_chain_type(
    llm            = llm,
    retriever      = vector_store.as_retriever(search_kwargs={"k":3}),
    chain_type_kwargs = {"prompt": NUMERIC_PROMPT},
    return_source_documents=False,
)

# ───────────────────────  SQLDatabaseChain  ────────────────────
sql_db = SQLDatabase.from_uri(
    PG_URI,
    include_tables=[SQL_TABLE, "district_percapita"],
)

# sql_db = SQLDatabase.from_uri(PG_URI)


sql_chain = SQLDatabaseChain.from_llm(llm, sql_db, verbose=True)

# ──────────────────────  Extremely-fast intent router  ─────────
_SQL_RE = re.compile(
    r"\b("
    r"list|show|give|display|top\s+\d+|rank|between|greater\s+than|less\s+than|"
    r"per\s*capita|kwh|k\s*wh|january|february|march|april|may|june|"
    r"july|august|september|october|november|december|\d{4}"
    r")\b",
    re.I,
)
def classify_intent(question:str)->str:
    return "SQL" if _SQL_RE.search(question) else "RAG"

# ───────────────────────────  Route  ───────────────────────────
@app.get("/qa", summary="Ask anything (auto-routes to RAG or SQL)")
def unified_qa(q: str = Query(..., description="Your question")):
    label = classify_intent(q)
    print(f"[INTENT] {label} | {q}")
    try:
        answer = sql_chain.run(q) if label=="SQL" else qa_chain.run(q)
    except Exception as e:
        err = str(e).splitlines()[0][:120]
        answer = f"(Error while executing query → {err})"
    return {"answer": answer}

# ────────────────────────────  main  ───────────────────────────
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
