import creds
from src.embedding.embedding import load_embedding
from src.ingest.uhj_messages import *
from src.redis.redis import create_index_from_documents


INDEX_NAME = "uhj"

docs = convert_uhj_messages_txts_to_documents()
rds = create_index_from_documents(docs, embedding=load_embedding(), index_name=INDEX_NAME)
rds.write_schema("data/schema/" + INDEX_NAME + ".yaml")