# Pipeline implementation for FAISS-based semantic search and summarization as a basis of comparison. For future work. 

import os
import time
import pickle
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import faiss

class FAISSSemanticQueryEngine:
    def __init__(
        self,
        csv_path: str,
        embedding_model: str = "all-MiniLM-L6-v2",
        top_k: int = 5,
        index_path: str = "faiss.index",
        metadata_path: str = "faiss_metadata.pkl",
        force_rebuild: bool = False,
    ):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in your .env file.")

        self.top_k = top_k
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = SentenceTransformer(embedding_model)
        self.llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)

        if not force_rebuild and os.path.exists(index_path) and os.path.exists(metadata_path):
            print("[FAISS] Loading precomputed index and metadata...")
            self.index = faiss.read_index(index_path)
            with open(metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            print("[FAISS] Building new index from CSV...")
            self.df = pd.read_csv(csv_path)
            self._build_index_from_dataframe()

    def _build_index_from_dataframe(self):
        abstracts = self.df["abstract"].fillna("").tolist()
        abstracts = [a for a in abstracts if len(a.strip()) > 10]

        print(f"[FAISS] Encoding {len(abstracts)} abstracts...")
        embeddings = self.model.encode(abstracts, show_progress_bar=True)

        dim = embeddings[0].shape[0]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))

        # Save index and metadata
        faiss.write_index(self.index, self.index_path)
        self.metadata = self.df[["title", "abstract", "authors_parsed"]].to_dict(orient="records")
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

        print("[FAISS] Index and metadata saved.")

    def query(self, query_text: str) -> dict:
        query_embedding = self.model.encode([query_text])
        D, I = self.index.search(np.array(query_embedding), self.top_k)
        matched = [self.metadata[i] for i in I[0]]

        context = "\n\n".join(
            f"Title: {doc['title']}\nAbstract: {doc['abstract']}" for doc in matched
        )

        prompt = f"""You are an AI assistant helping summarize research papers. Based on the following abstracts, summarize the key findings and themes relevant to the query: '{query_text}'.

Context:
{context}

Summary:
"""

        start_time = time.time()
        response = self.llm.invoke([HumanMessage(content=prompt)])
        end_time = time.time()

        return {
            "query": query_text,
            "response": response.content,
            "latency_sec": round(end_time - start_time, 2),
            "num_docs": len(matched),
            "token_estimate": len(prompt.split()) + len(response.content.split())
        }
