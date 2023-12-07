import docx2txt
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from typing import AnyStr


def get_text_from_file(
        file,
        filetype: AnyStr = "pdf",
        out: AnyStr = "str"
    ):
    if filetype == "pdf":
        pdf = PdfReader(file)
        output = []
        for page in pdf.pages:
            text = page.extract_text()
            # text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
            # text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
            # text = re.sub(r"\n\s*\n", "\n\n", text)
            output.append(text)
        if out == "str":
            return "\n\n".join(output)
        return output
    elif filetype == "docx":
        text = docx2txt.process(file)
        # text = re.sub(r"\n\s*\n", "\n\n", text)
        return text
    
def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")

def get_all_read_online_url_exts(base_url):
    messages = list()
    response = requests.get(base_url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    for row in soup.find_all("tr", class_="document-row"):
        summary = row.text.strip()
        url_tail = row.find("a")["href"]
        messages.append([url_tail, summary])
    return messages

def text_to_docs(
        text: AnyStr,
        filename: AnyStr
):
    if isinstance(text, str):
        text = [text]

    # docs = [Document(page_content=page) for page in text]

    # for i in range(len(docs)):
    #     docs[i].metadata["page"] = i + 1

    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            # chunk_overlap=200
        )
    docs = []
    for page in text:
        chunks = text_splitter.split_text(page)
        for i in range(len(chunks)):
            doc = Document(page_content=chunks[i], metadata={"filename": filename})
            docs.append(doc)
    return docs