import os
import ast
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_graph_retriever import GraphRetriever
from graph_retriever.strategies import Eager
from langchain_graph_retriever.adapters.chroma import ChromaAdapter
from langchain_core.messages import HumanMessage 


class GraphRAGQueryEngine:
    def __init__(self, csv_path: str):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in your .env file.")
        
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)
        self.documents = self._load_documents(csv_path)
        self.vector_store = Chroma.from_documents(self.documents, self.embeddings)
        self.store_adapter = ChromaAdapter(self.vector_store)

        edges = [("categories", "categories")]
        strategy = Eager(k=5, start_k=1, max_depth=2)
        self.graph_retriever = GraphRetriever(store=self.store_adapter, edges=edges, strategy=strategy)

    def _load_documents(self, csv_path: str):
        df = pd.read_csv(csv_path)
        documents = []
        for _, row in df.iterrows():
            title = row.get('title', '')
            abstract = row.get('abstract', '')
            categories_raw = row.get('categories', '')
            authors_parsed = ast.literal_eval(row.get('authors_parsed', '[]'))
            update_date = row.get('update_date', '')

            categories = categories_raw.split() if isinstance(categories_raw, str) else []
            authors = ", ".join([" ".join(a[:2]) for a in authors_parsed])

            content = f"""Title: {title}
Abstract: {abstract}
Categories: {', '.join(categories)}
Authors: {authors}
Date: {update_date}
"""

            documents.append(Document(
                page_content=content,
                metadata={
                    "id": str(row["id"]),
                    "categories": ", ".join(categories)
                }
            ))
        return documents

    def query(self, query_text: str) -> str:
        retrieved_docs = self.graph_retriever.invoke(query_text)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        prompt = f"""Use the following context to answer the question.

Context:
{context}

Question:
{query_text}

Answer:"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
