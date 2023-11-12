import gradio as gr
from langchain.vectorstores.redis import Redis
from src.embedding.embedding import load_embedding

INDEX_NAME = "uhj"

rds = Redis.from_existing_index(
    index_name="uhj", 
    embedding=load_embedding(), 
    redis_url="redis://localhost:6379", 
    schema="data/schema/" + INDEX_NAME + ".yaml"
    )

def get_sources(query, num):
    docs = rds.similarity_search(query, k=int(num))
    return '\n\n'.join([doc.page_content for doc in docs])

with gr.Blocks() as demo:
    query = gr.Textbox(label="Query", placeholder="Ask a question here...")
    num = gr.Number(label="Number of sources (paragraphs) to retrieve")
    output = gr.TextArea(label="Sources", placeholder="Retrieved sources will appear here")
    submit = gr.Button("Retrieve")
    submit.click(fn=get_sources, inputs=[query, num], outputs=output)
    
if __name__ == "__main__":
    demo.launch(share=True)   
