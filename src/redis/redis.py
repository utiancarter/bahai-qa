from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis
import redis
from typing import AnyStr, List


def create_index_from_documents(
        docs: List[Document], 
        embedding: OpenAIEmbeddings,
        index_name: AnyStr
    ):
    return Redis.from_documents(docs, embedding=embedding, redis_url="redis://localhost:6379", index_name=index_name)