from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import creds
import gradio as gr
from langchain.vectorstores.redis import Redis
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms.openai import OpenAI
from src.embedding.embedding import load_embedding
from typing import Dict, Union, List


INDEX_NAME = "uhj"

PROMPT = """You're a retrieve augmented chatbot. You answer user's questions based only on the context provided by the user. The context is broken up into paragraphs, each of which has an accompanying date in YYYYMMDD format on which the paragraph was written, an addressee, and a short summary of the letter in which the paragraph can be found.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
You must answer the question completely given the context.

User's question is: {input_question}

Context is: {input_context}
"""

class RedisRetrieveUserProxyAgent(RetrieveUserProxyAgent):
    def query_vector_db(
        self,
        query_texts: List[str],
        n_results: int = 10,
        search_string: str = "",
        **kwargs,
    ) -> Dict[str, Union[List[str], List[List[str]]]]:
        rds = Redis.from_existing_index(
            index_name="uhj", 
            embedding=load_embedding(), 
            redis_url="redis://localhost:6379", 
            schema="data/schema/" + INDEX_NAME + ".yaml"
            )
        docs = rds.similarity_search(query=query_texts, k=n_results)
        compatible_docs = {
            'ids': [[doc.metadata['id'] for doc in docs]],
            'documents': [[doc.page_content for doc in docs]]
        }
        return compatible_docs

    def retrieve_docs(self, problem: str, n_results: int = 20, search_string: str = "", **kwargs):
        results = self.query_vector_db(
            query_texts=problem,
            n_results=n_results,
            search_string=search_string,
            **kwargs,
        )

        self._results = results
        print("doc_ids: ", results["ids"])

# llm = OpenAI(
#     openai_api_key=creds.OPENAI_API_KEY,
#     temperature=0.0
# )

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

llm_config = {
    "timeout": 120,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

user_proxy = RedisRetrieveUserProxyAgent(
    name="User_proxy",
    is_termination_msg=termination_msg,
    # system_message="Assistant who has extra content retrieval power for finding relevant context to answer questions.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    retrieve_config={
        "task": "qa",
        "model": config_list[0]["model"],
        "customized_prompt": PROMPT,
        "update_context": False
    },
    code_execution_config=False,  # we don't want to execute code in this case.
)

researcher = RetrieveAssistantAgent(
    name="Researcher",
    is_termination_msg=termination_msg,
    system_message="You are a helpful researcher who will synthesize a response based on the context given. If you need more information, you should ask new questions requesting the information you need. You must not rely on any outside knowledge to answer the question. Reply `TERMINATE` in the end when everything is done.",
    llm_config=llm_config,
)

def get_response(task, n_results):
    user_proxy.initiate_chat(researcher, problem=task, n_results=int(n_results))
    return user_proxy.chat_messages[researcher][-3]['content']

# task = "How can we show trustworthiness?"

# user_proxy.initiate_chat(researcher, problem=task, n_results=50)

with gr.Blocks() as demo:
    query = gr.Textbox(label="Query", placeholder="Ask a question here...")
    num = gr.Number(label="Number of sources (paragraphs) to retrieve", value=25, interactive=False)
    output = gr.TextArea(label="Response", placeholder="The generated response will appear here")
    submit = gr.Button("Generate")
    submit.click(fn=get_response, inputs=[query, num], outputs=output)

if __name__ == "__main__":
    demo.launch(share=True)