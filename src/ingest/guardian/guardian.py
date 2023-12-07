from bs4 import BeautifulSoup
from langchain.docstore.document import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.ingest.ingest import get_all_read_online_url_exts, get_soup
from src.ingest.guardian.handlers import *
import json
import os
from typing import Dict, List, AnyStr, Union


BAHAI_HOMEPAGE = "https://www.bahai.org"

def get_all_read_online_url_exts(base_url):
    urls = list()
    soup = get_soup(base_url)
    for item in soup.find_all('div', class_="expandablelist-item"):
        info_url = BAHAI_HOMEPAGE + item.h4.a['href']
        urls.append(info_url)
    return urls

def get_guardian_message_data_from_html(url):
    print("Parsing: " + url)
    metadata = dict()
    soup = get_soup(url)
    metadata["title"] = soup.find('h1', class_="publication-page-title").text.strip()
    metadata["summary"] = soup.find('p', class_="truncated js-publication-description").text.strip()
    
    content_url = "https://www.bahai.org" + [link['href'] for link in soup.find_all('a', class_='js-download-link js-track-link') if 'html' in link['href']][0]
    content_soup = get_soup(content_url)
    handler = handlers[metadata["title"]]
    texts = handler(content_soup)

    # Add title and summary to metadata
    metadata.update(texts)
    return metadata

# def save_to_txt(filepath, paragraph_texts, metadata):
#     with open(filepath, 'w', encoding="utf-8") as f:
#         for detail in metadata.values():
#             f.write(detail +'\n')
#         for par in paragraph_texts:
#             f.write(par + '\n')

def save_to_json(filepath: str, json_object: Dict):
    with open(filepath, 'w', encoding="utf-8") as f:
        json.dump(json_object, f)

# def save_all_guardian_messages_as_txts():
#     base_url = "https://www.bahai.org/library/authoritative-texts/shoghi-effendi/"
#     urls = get_all_read_online_url_exts(base_url)
#     for url in urls[:2]: ######################################## REMOVE SLICE
#         texts, metadata = get_guardian_message_data_from_html(url)
#         volume = url.split("/")[-2].replace("-", "_")
        
#         # Analyze dimensions of list of paragraph_texts to either save to one file or multiple files
#         list_of_lists = len([l for l in texts if type(l) == list]) > 0
#         if list_of_lists:
#             for letter_texts in texts:
#                 letter_name = letter_texts[0].split('\n')[0].lower().replace(" ", "_").replace(",", "")
#                 save_to_txt('data/guardian/' + volume + "_" + letter_name + '.txt', letter_texts, metadata)
#         else:
#             save_to_txt('data/guardian/' + volume + '.txt', texts, metadata)

def save_all_guardian_messages_as_json():
    base_url = "https://www.bahai.org/library/authoritative-texts/shoghi-effendi/"
    urls = get_all_read_online_url_exts(base_url)
    for url in urls:
        json_texts = get_guardian_message_data_from_html(url)
        volume = url.split("/")[-2].replace("-", "_")
        save_to_json('data/guardian/' + volume + '.json', json_texts)
        # Analyze dimensions of list of paragraph_texts to either save to one file or multiple files
        # if list_of_lists:
        #     for letter_texts in texts:
        #         letter_name = letter_texts[0].split('\n')[0].lower().replace(" ", "_").replace(",", "")
        #         save_to_txt('data/guardian/' + volume + "_" + letter_name + '.txt', letter_texts, metadata)
        # else:
        #     save_to_txt('data/guardian/' + volume + '.txt', texts, metadata)

def create_document(join_list: List, metadata: Dict, join_sep: AnyStr='\n'):
    chunk = join_sep.join(join_list)
    doc = Document(page_content=chunk, metadata=metadata)
    return doc

def explore_contents(docs: List, join_list: List, content_list: List, metadata: Dict):
    for content in content_list:
        new_join_list = [x for x in join_list]
        if type(content) == dict:
            new_join_list = new_join_list + [v for v in content.values() if type(v) != list]
            docs = explore_contents(docs, new_join_list, content["contents"], metadata)
        elif type(content) == list:
            docs.append(create_document(new_join_list + content, metadata))
        else:
            docs.append(create_document(new_join_list + [content], metadata))
    return docs

# def traverse_json(d):
#     non_content_keys = [k for k in d.keys() if k != "contents"]
#     for k, v in d.items():


def convert_guardian_messages_json_to_documents():
    docs = list()
    for folder, _, files in os.walk('data/guardian'):
        for file in files:
            fp = folder + '/' + file
            with open(fp, 'r', encoding='utf-8') as f:
                text = json.load(f)
            
            metadata = {
                "author": "Guardian",
                "title": text["title"]
            }

            book_level_join_list = [metadata["title"], text["summary"]]
            docs = explore_contents(docs, book_level_join_list, text["contents"], metadata)
    return docs