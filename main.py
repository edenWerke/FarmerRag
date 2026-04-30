# from fastapi import FastAPI
# from pydantic import BaseModel
# from groq import Groq
# from dotenv import load_dotenv
# import os

# # load env
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# print("KEY:", GROQ_API_KEY)
# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing in .env")

# app = FastAPI()

# client = Groq(api_key=GROQ_API_KEY)

# # load knowledge
# try:
#     with open("agriculture.txt", "r", encoding="utf-8") as f:
#         knowledge = f.read()
# except:
#     knowledge = "No agriculture data found."

# class Query(BaseModel):
#     question: str

# @app.get("/")
# def home():
#     return {"message": "🌾 Farmer AI running"}

# @app.post("/chat")
# def chat(query: Query):

#     print("🔥 MODEL USED: llama-3.1-8b-instant")  # ✅ correct place

#     try:
#         response = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": f"""You are a FARMING ASSISTANT... {knowledge}"""
#                 },
#                 {
#                     "role": "user",
#                     "content": query.question
#                 }
#             ]
#         )

#         return {"answer": response.choices[0].message.content}

#     except Exception as e:
#         print("ERROR:", e)
#         return {"error": str(e)}
# from fastapi import FastAPI
# from pydantic import BaseModel
# from groq import Groq
# from dotenv import load_dotenv
# import os
# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer

# # ======================
# # LOAD ENV
# # ======================
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing in .env")

# client = Groq(api_key=GROQ_API_KEY)

# app = FastAPI()

# # ======================
# # EMBEDDING MODEL
# # ======================
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# # ======================
# # LOAD KNOWLEDGE
# # ======================
# try:
#     with open("agriculture.txt", "r", encoding="utf-8") as f:
#         text = f.read()
# except:
#     text = "No agriculture data found."

# # ======================
# # SPLIT TEXT INTO CHUNKS
# # ======================
# def split_text(text, chunk_size=100):
#     sentences = text.split(".")
#     chunks = []
#     current_chunk = ""

#     for sentence in sentences:
#         sentence = sentence.strip()
#         if not sentence:
#             continue

#         if len(current_chunk.split()) + len(sentence.split()) < chunk_size:
#             current_chunk += sentence + ". "
#         else:
#             chunks.append(current_chunk.strip())
#             current_chunk = sentence + ". "

#     if current_chunk:
#         chunks.append(current_chunk.strip())

#     return chunks

# # remove duplicates
# chunks = list(set(split_text(text)))

# # ======================
# # LOAD / CREATE FAISS INDEX (PERSISTENCE)
# # ======================
# if os.path.exists("faiss.index") and os.path.exists("chunks.npy"):
#     index = faiss.read_index("faiss.index")
#     chunks = np.load("chunks.npy", allow_pickle=True).tolist()
# else:
#     embeddings = embed_model.encode(chunks)
#     embeddings = np.array(embeddings)

#     dimension = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)

#     # save for reuse
#     faiss.write_index(index, "faiss.index")
#     np.save("chunks.npy", chunks)

# # ======================
# # RETRIEVAL FUNCTION
# # ======================
# def retrieve(query, k=3):
#     query_vec = embed_model.encode([query])
#     query_vec = np.array(query_vec)

#     distances, indices = index.search(query_vec, k * 3)

#     seen = set()
#     results = []

#     for dist, i in zip(distances[0], indices[0]):
#         chunk = chunks[i]

#         # 🔥 filter irrelevant matches
#         if dist > 1.5:
#             continue

#         if chunk not in seen:
#             results.append(chunk)
#             seen.add(chunk)

#         if len(results) == k:
#             break

#     return results

# # ======================
# # REQUEST MODEL
# # ======================
# class Query(BaseModel):
#     question: str

# # ======================
# # ROUTES
# # ======================
# @app.get("/")
# def home():
#     return {"message": "🌾 Farmer AI RAG is running"}

# @app.post("/chat")
# def chat(query: Query):
#     try:
#         # STEP 1: retrieve relevant knowledge
#         docs = retrieve(query.question)

#         # 🔥 handle empty retrieval
#         if not docs:
#             return {
#                 "answer": "I don't know based on available data",
#                 "context_used": []
#             }

#         context = "\n".join(docs)

#         # STEP 2: send to LLM
#         response = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": f"""
# You are a FARMING EXPERT AI.

# STRICT RULES:
# - Answer ONLY using the context
# - If answer is not in context, say: "I don't know based on available data"
# - Do NOT guess
# - Give short, practical advice for farmers

# CONTEXT:
# {context}
# """
#                 },
#                 {
#                     "role": "user",
#                     "content": query.question
#                 }
#             ]
#         )

#         return {
#             "answer": response.choices[0].message.content,
#             "context_used": docs
#         }

#     except Exception as e:
#         return {"error": str(e)}
# from fastapi import FastAPI
# from pydantic import BaseModel
# from groq import Groq
# from dotenv import load_dotenv
# import os
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer

# # ======================
# # LOAD ENV
# # ======================
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing in .env")

# client = Groq(api_key=GROQ_API_KEY)

# app = FastAPI()

# # ======================
# # LOAD KNOWLEDGE
# # ======================
# try:
#     with open("agriculture.txt", "r", encoding="utf-8") as f:
#         text = f.read()
# except:
#     text = "No agriculture data found."

# # ======================
# # SPLIT TEXT INTO CHUNKS
# # ======================
# def split_text(text, chunk_size=100):
#     sentences = text.split(".")
#     chunks = []
#     current_chunk = ""

#     for sentence in sentences:
#         sentence = sentence.strip()
#         if not sentence:
#             continue

#         if len(current_chunk.split()) + len(sentence.split()) < chunk_size:
#             current_chunk += sentence + ". "
#         else:
#             chunks.append(current_chunk.strip())
#             current_chunk = sentence + ". "

#     if current_chunk:
#         chunks.append(current_chunk.strip())

#     return chunks

# chunks = list(set(split_text(text)))

# # ======================
# # TF-IDF EMBEDDINGS (LIGHTWEIGHT)
# # ======================
# vectorizer = TfidfVectorizer()
# embeddings = vectorizer.fit_transform(chunks).toarray()

# # ======================
# # RETRIEVAL FUNCTION
# # ======================
# def retrieve(query, k=3):
#     query_vec = vectorizer.transform([query]).toarray()

#     scores = np.dot(embeddings, query_vec.T).flatten()

#     top_indices = scores.argsort()[-k:][::-1]

#     return [chunks[i] for i in top_indices]

# # ======================
# # REQUEST MODEL
# # ======================
# class Query(BaseModel):
#     question: str

# # ======================
# # ROUTES
# # ======================
# @app.get("/")
# def home():
#     return {"message": "🌾 Farmer AI RAG is running"}

# @app.post("/chat")
# def chat(query: Query):
#     try:
#         docs = retrieve(query.question)

#         if not docs:
#             return {
#                 "answer": "I don't know based on available data",
#                 "context_used": []
#             }

#         context = "\n".join(docs)

#         response = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": f"""
# You are a FARMING EXPERT AI.

# STRICT RULES:
# - Answer ONLY using the context
# - If answer is not in context, say: "I don't know based on available data"
# - Do NOT guess
# - Give short, practical advice

# CONTEXT:
# {context}
# """
#                 },
#                 {
#                     "role": "user",
#                     "content": query.question
#                 }
#             ]
#         )

#         return {
#             "answer": response.choices[0].message.content,
#             "context_used": docs
#         }

#     except Exception as e:
#         return {"error": str(e)}
# from fastapi import FastAPI
# from pydantic import BaseModel
# from groq import Groq
# from dotenv import load_dotenv
# import os
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from pypdf import PdfReader
# import re

# # ======================
# # LOAD ENV
# # ======================
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing")

# client = Groq(api_key=GROQ_API_KEY)

# app = FastAPI()
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # ======================
# # PDF LOADER (CLEAN)
# # ======================
# def load_pdf_text(path):
#     try:
#         reader = PdfReader(path)
#         text = ""
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#         return text
#     except Exception as e:
#         print("PDF ERROR:", e)
#         return ""

# # ======================
# # LOAD DATA
# # ======================
# texts = []

# try:
#     with open("agriculture.txt", "r", encoding="utf-8") as f:
#         txt = f.read()
#         print("📘 TXT LOADED:", len(txt))
#         texts.append(txt)
# except:
#     print("TXT NOT FOUND")

# pdf_text = load_pdf_text("amharic_guide.pdf")
# print("📄 PDF LOADED:", len(pdf_text))
# texts.append(pdf_text)

# full_text = "\n".join(texts)

# # ======================
# # SMART CHUNKING (IMPORTANT FIX)
# # ======================
# def split_text(text):
#     lines = text.split("\n")
#     chunks = []

#     for line in lines:
#         line = line.strip()

#         # remove garbage unicode chunks
#         if len(line) < 20:
#             continue

#         # clean weird pdf artifacts
#         line = re.sub(r'[^a-zA-Z0-9\u1200-\u137F\s.,]', '', line)

#         chunks.append(line)

#     print("🧩 CHUNKS:", len(chunks))
#     return chunks

# chunks = split_text(full_text)

# # ======================
# # TF-IDF VECTOR STORE
# # ======================
# vectorizer = TfidfVectorizer(
#     lowercase=True,
#     stop_words=None
# )

# embeddings = vectorizer.fit_transform(chunks).toarray()

# print("⚙️ VECTOR READY:", embeddings.shape)

# # ======================
# # LANGUAGE DETECTION
# # ======================
# def is_amharic(text):
#     return any("\u1200" <= c <= "\u137F" for c in text)

# # ======================
# # HYBRID RETRIEVAL (V2 CORE)
# # ======================
# def retrieve(query, k=3):
#     query_vec = vectorizer.transform([query]).toarray()

#     # TF-IDF similarity
#     tfidf_scores = np.dot(embeddings, query_vec.T).flatten()

#     query_words = set(query.lower().split())

#     scored = []

#     for i, chunk in enumerate(chunks):

#         chunk_words = set(chunk.lower().split())

#         # keyword overlap (VERY IMPORTANT UPGRADE)
#         overlap = len(query_words.intersection(chunk_words))

#         # final hybrid score
#         score = tfidf_scores[i] + (overlap * 2)

#         scored.append((score, chunk))

#     # sort best matches
#     scored.sort(reverse=True, key=lambda x: x[0])

#     results = [c for s, c in scored if s > 0][:k]

#     print("🔍 RETRIEVED:", results)

#     return results

# # ======================
# # REQUEST MODEL
# # ======================
# class Query(BaseModel):
#     question: str

# # ======================
# # ROUTES
# # ======================
# @app.get("/")
# def home():
#     return {"message": "🌾 Farmer AI RAG v2 running"}

# @app.post("/chat")
# def chat(query: Query):

#     print("\n====================")
#     print("QUESTION:", query.question)

#     docs = retrieve(query.question)

#     print("DOCS FOUND:", len(docs))

#     if not docs:
#         return {
#             "answer": "I don't know based on available data",
#             "context_used": []
#         }

#     context = "\n".join(docs)

#     language = "Amharic" if is_amharic(query.question) else "English"

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": f"""
# You are a FARMING EXPERT AI.

# Language: {language}

# RULES:
# - Use ONLY the context
# - DO NOT hallucinate
# - If answer is missing say: "I don't know based on available data"
# - Be simple and practical

# CONTEXT:
# {context}
# """
#             },
#             {
#                 "role": "user",
#                 "content": query.question
#             }
#         ]
#     )

#     return {
#         "answer": response.choices[0].message.content,
#         "context_used": docs
#     }
# from fastapi import FastAPI
# from pydantic import BaseModel
# from groq import Groq
# from dotenv import load_dotenv
# import os
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from pypdf import PdfReader
# import re

# # ======================
# # LOAD ENV
# # ======================
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing")

# client = Groq(api_key=GROQ_API_KEY)

# app = FastAPI()

# # ======================
# # GLOBAL VARIABLES
# # ======================
# vectorizer = None
# embeddings = None
# chunks = []
# full_text = ""

# # ======================
# # FILE PATH SAFE (IMPORTANT FOR RENDER)
# # ======================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# TXT_PATH = os.path.join(BASE_DIR, "agriculture.txt")
# PDF_PATH = os.path.join(BASE_DIR, "amharic_guide.pdf")

# # ======================
# # PDF LOADER
# # ======================
# def load_pdf_text(path):
#     try:
#         reader = PdfReader(path)
#         text = ""
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#         return text
#     except Exception as e:
#         print("❌ PDF ERROR:", e)
#         return ""

# # ======================
# # CLEAN + CHUNK TEXT
# # ======================
# def split_text(text):
#     lines = text.split("\n")
#     chunks = []

#     for line in lines:
#         line = line.strip()

#         if len(line) < 20:
#             continue

#         line = re.sub(r'[^a-zA-Z0-9\u1200-\u137F\s.,]', '', line)
#         chunks.append(line)

#     return chunks

# # ======================
# # INIT MODEL (CRITICAL FIX → RUN ON STARTUP)
# # ======================
# @app.on_event("startup")
# def startup():
#     global vectorizer, embeddings, chunks, full_text

#     print("🚀 STARTING FARMER RAG...")

#     texts = []

#     # ---- TXT ----
#     try:
#         with open(TXT_PATH, "r", encoding="utf-8") as f:
#             txt = f.read()
#             print("📘 TXT LOADED:", len(txt))
#             texts.append(txt)
#     except Exception as e:
#         raise RuntimeError(f"TXT load failed: {e}")

#     # ---- PDF ----
#     pdf_text = load_pdf_text(PDF_PATH)
#     print("📄 PDF LOADED:", len(pdf_text))
#     texts.append(pdf_text)

#     full_text = "\n".join(texts)

#     # ---- CHUNK ----
#     chunks = split_text(full_text)
#     print("🧩 CHUNKS:", len(chunks))

#     if len(chunks) == 0:
#         raise ValueError("No chunks generated! Check dataset.")

#     # ---- TF-IDF ----
#     vectorizer = TfidfVectorizer(lowercase=True)
#     embeddings = vectorizer.fit_transform(chunks).toarray()

#     print("⚙️ VECTOR READY:", embeddings.shape)

# # ======================
# # LANGUAGE DETECTION
# # ======================
# def is_amharic(text):
#     return any("\u1200" <= c <= "\u137F" for c in text)

# # ======================
# # RETRIEVAL ENGINE
# # ======================
# def retrieve(query, k=3):
#     query_vec = vectorizer.transform([query]).toarray()

#     tfidf_scores = np.dot(embeddings, query_vec.T).flatten()

#     query_words = set(query.lower().split())

#     scored = []

#     for i, chunk in enumerate(chunks):
#         chunk_words = set(chunk.lower().split())
#         overlap = len(query_words.intersection(chunk_words))

#         score = tfidf_scores[i] + (overlap * 2)
#         scored.append((score, chunk))

#     scored.sort(reverse=True, key=lambda x: x[0])

#     return [c for s, c in scored if s > 0][:k]

# # ======================
# # REQUEST MODEL
# # ======================
# class Query(BaseModel):
#     question: str

# # ======================
# # ROUTES
# # ======================
# @app.get("/")
# def home():
#     return {"message": "🌾 Farmer AI RAG running successfully"}

# @app.post("/chat")
# def chat(query: Query):

#     print("\n====================")
#     print("QUESTION:", query.question)

#     docs = retrieve(query.question)

#     if not docs:
#         return {
#             "answer": "I don't know based on available data",
#             "context_used": []
#         }

#     context = "\n".join(docs)

#     language = "Amharic" if is_amharic(query.question) else "English"

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": f"""
# You are a FARMING EXPERT AI.

# Language: {language}

# RULES:
# - Use ONLY the context
# - DO NOT hallucinate
# - If answer is missing say: "I don't know based on available data"
# - Be simple and practical

# CONTEXT:
# {context}
# """
#             },
#             {
#                 "role": "user",
#                 "content": query.question
#             }
#         ]
#     )

#     return {
#         "answer": response.choices[0].message.content,
#         "context_used": docs
#     }
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from pypdf import PdfReader
import re

# ======================
# LOAD ENV
# ======================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY missing")

client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

# ======================
# GLOBALS
# ======================
vectorizer = None
embeddings = None
chunks = []
full_text = ""
# hello world
# ======================
# PATHS
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("\n📍 BASE DIR:", BASE_DIR)
print("📁 FILES:", os.listdir(BASE_DIR))
TXT_PATH = os.path.join(BASE_DIR, "agriculture.txt")
PDF_PATH = os.path.join(BASE_DIR, "amharic_guide.pdf")

# ======================
# DEBUG PRINT HELPERS
# ======================
def debug(msg):
    print(f"\n🔍 DEBUG: {msg}")

# ======================
# PDF LOADER
# ======================
def load_pdf_text(path):
    debug(f"Checking PDF path: {path}")
    if not os.path.exists(path):
        print("❌ PDF NOT FOUND!")
        return ""

    try:
        reader = PdfReader(path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        print("❌ PDF ERROR:", e)
        return ""

# ======================
# CHUNKING
# ======================
def split_text(text):
    lines = text.split("\n")
    chunks = []

    for line in lines:
        line = line.strip()

        if len(line) < 20:
            continue

        line = re.sub(r'[^a-zA-Z0-9\u1200-\u137F\s.,]', '', line)
        chunks.append(line)

    return chunks

# ======================
# STARTUP
# ======================
@app.on_event("startup")
def startup():
    global vectorizer, embeddings, chunks, full_text

    print("\n🚀 STARTUP STARTED")

    # ======================
    # CHECK FILES
    # ======================
    print("\n📂 FILE CHECK:")
    print("TXT exists:", os.path.exists(TXT_PATH))
    print("PDF exists:", os.path.exists(PDF_PATH))

    # ======================
    # LOAD TXT
    # ======================
    try:
        with open(TXT_PATH, "r", encoding="utf-8") as f:
            txt = f.read()
            print("📘 TXT LOADED:", len(txt))
    except Exception as e:
        raise RuntimeError(f"TXT ERROR: {e}")

    # ======================
    # LOAD PDF
    # ======================
    pdf_text = load_pdf_text(PDF_PATH)
    print("📄 PDF LOADED:", len(pdf_text))

    # ======================
    # MERGE TEXT
    # ======================
    full_text = txt + "\n" + pdf_text

    # ======================
    # CHUNK
    # ======================
    chunks = split_text(full_text)
    print("🧩 CHUNKS:", len(chunks))

    if len(chunks) == 0:
        raise ValueError("❌ No chunks generated!")

    # ======================
    # VECTORIZE
    # ======================
    vectorizer = TfidfVectorizer()
    embeddings = vectorizer.fit_transform(chunks).toarray()

    print("⚙️ VECTOR READY:", embeddings.shape)

    print("\n✅ STARTUP COMPLETE")

# ======================
# REQUEST MODEL
# ======================
class Query(BaseModel):
    question: str

# ======================
# RETRIEVAL (DEBUG VERSION)
# ======================
def retrieve(query, k=3):
    debug(f"QUERY: {query}")

    if vectorizer is None:
        print("❌ VECTOR NOT READY")
        return []

    query_vec = vectorizer.transform([query]).toarray()

    scores = np.dot(embeddings, query_vec.T).flatten()

    scored_chunks = []

    for i, chunk in enumerate(chunks):
        scored_chunks.append((scores[i], chunk))

    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    print("\n📊 TOP SCORES:")

    for i in range(min(5, len(scored_chunks))):
        print(scored_chunks[i][0], "=>", scored_chunks[i][1][:80])

    top = [c for _, c in scored_chunks[:k]]

    return top

# ======================
# ROUTES
# ======================
@app.get("/")
def home():
    return {"message": "🌾 DEBUG FARMER RAG RUNNING"}

@app.post("/chat")
def chat(query: Query):

    print("\n====================")
    print("QUESTION:", query.question)

    docs = retrieve(query.question)

    print("\n📚 RETRIEVED DOCS:", len(docs))

    if not docs:
        return {
            "answer": "❌ No relevant data found (DEBUG MODE)",
            "context_used": []
        }

    context = "\n".join(docs)

    print("\n🧠 CONTEXT USED:\n", context[:300])

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are a farming expert AI.
Use ONLY the context.

CONTEXT:
{context}
"""
                },
                {
                    "role": "user",
                    "content": query.question
                }
            ]
        )

        answer = response.choices[0].message.content

    except Exception as e:
        print("❌ GROQ ERROR:", e)
        return {"answer": "Groq API failed", "error": str(e)}

    return {
        "answer": answer,
        "context_used": docs
    }