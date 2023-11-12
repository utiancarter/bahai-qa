from langchain.embeddings import OpenAIEmbeddings
import creds


def load_embedding():
    return OpenAIEmbeddings(
        openai_api_key=creds.OPENAI_API_KEY,
        model="text-embedding-ada-002",
        chunk_size=1
    )