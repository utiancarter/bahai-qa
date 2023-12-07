from typing import AnyStr, Dict, List, Tuple, Union

import gradio as gr
from langchain.vectorstores.redis import Redis
from langchain.docstore.document import Document
from src.embedding.embedding import load_embedding


CHOICES = ["Guardian", "Universal House of Justice"]
CHOICE_TO_INDEX = {
    "Universal House of Justice": "uhj",
    "Guardian": "guardian"
}

def get_rds(index_choice: AnyStr):
    index_name = CHOICE_TO_INDEX[index_choice]
    rds = Redis.from_existing_index(
        index_name=index_name, 
        embedding=load_embedding(), 
        redis_url="redis://localhost:6379", 
        schema="data/schema/" + index_name + ".yaml"
        )
    return rds

def get_single_source(query: AnyStr, num: int, index_choice: AnyStr):
    docs = get_rds(index_choice=index_choice).similarity_search(query, k=int(num))
    return '\n\n'.join([doc.page_content for doc in docs])

def get_sources(query: AnyStr, num: int, index_choices: List[AnyStr]):
    num = int(num)
    all_docs_with_scores: List[Tuple[Document, float]] = list()
    for index_choice in index_choices:
        all_docs_with_scores += get_rds(index_choice=index_choice).similarity_search_with_relevance_scores(query, k=num)
    all_docs_with_scores.sort(key=lambda tup: tup[1], reverse=True)
    docs = [doc[0] for doc in all_docs_with_scores[:num]]
    return '\n\n'.join([doc.page_content for doc in docs])

with gr.Blocks() as demo:
    with gr.Row():
        query = gr.Textbox(label="Query", placeholder="Ask a question here...")
        num = gr.Number(label="Number of sources (paragraphs) to retrieve", value=20)
        # index_choice = gr.Radio(choices=CHOICES, label="Choose the source to use")
        index_choices = gr.CheckboxGroup(choices=CHOICES, label="Choose the sources to use")
    with gr.Row():
        submit = gr.Button("Retrieve")
    with gr.Row():
        output = gr.TextArea(label="Sources", placeholder="Retrieved sources will appear here", autoscroll=False)
    
    # submit.click(fn=get_single_source, inputs=[query, num, index_choice], outputs=output)
    submit.click(fn=get_sources, inputs=[query, num, index_choices], outputs=output)
    
if __name__ == "__main__":
    # demo.launch(share=True)
    demo.launch()
