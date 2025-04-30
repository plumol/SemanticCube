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

# load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     raise ValueError("OPENAI_API_KEY not set in your .env file.")

# llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)
# embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)

# df = pd.read_csv("../dataset/clean_fields_filter_date_sample50.csv")
# documents = []

# documents = []

# for _, row in df.iterrows():
#     # Parse fields
#     title = row.get('title', '')
#     abstract = row.get('abstract', '')
#     categories_raw = row.get('categories', '')
#     authors_parsed = ast.literal_eval(row.get('authors_parsed', '[]'))
#     update_date = row.get('update_date', '')

#     # Clean + structure
#     categories = categories_raw.split() if isinstance(categories_raw, str) else []
#     authors = ", ".join([" ".join(a[:2]) for a in authors_parsed])

#     # Create content block
#     content = f"""Title: {title}
# Abstract: {abstract}
# Categories: {', '.join(categories)}
# Authors: {authors}
# Date: {update_date}
# """

#     # Append Document
#     documents.append(Document(
#         page_content=content,
#         metadata={
#             "id": str(row["id"]),
#             "categories": ", ".join(categories)
#         }
#     ))

# vector_store = Chroma.from_documents(documents, embeddings)
# store_adapter = ChromaAdapter(vector_store)

# print(f"Loaded {len(documents)} documents from CSV file.")
# print("Building knowledge graph...")

# edges = [("categories", "categories")]
# strategy = Eager(k=5, start_k=1, max_depth=2)
# graph_retriever = GraphRetriever(store=store_adapter, edges=edges, strategy=strategy)

# # Query the knowledge graph
# query = "What were the significant findings of AI papers before 2024?"
# retrieved_docs = graph_retriever.invoke(query)

# # Generate response using LLM
# context = "\n\n".join([doc.page_content for doc in retrieved_docs])
# prompt = f"""Use the following context to answer the question.

# Context:
# {context}

# Question:
# {query}

# Answer:"""

# response = llm.invoke([HumanMessage(content=prompt)])
# print(response.content)

# graphrag_engine.py


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
