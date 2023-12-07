import creds
from src.embedding.embedding import load_embedding
from src.ingest.guardian.guardian import *
from src.redis.redis import create_index_from_documents


INDEX_NAME = "guardian"


# save_all_guardian_messages_as_txts()
# save_all_guardian_messages_as_json()
docs = convert_guardian_messages_json_to_documents()
rds = create_index_from_documents(docs, embedding=load_embedding(), index_name=INDEX_NAME)
rds.write_schema("data/schema/" + INDEX_NAME + ".yaml")