from bs4 import BeautifulSoup
from langchain.docstore.document import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import requests


def get_message_data_from_html(html):
    print("Parsing: " + html)
    response = requests.get(html)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    date = html.split("/")[-2].split("_")[0]
    # date_header_class = "brl-muhj-opening-date"
    # # date = soup.find("p", class_=date_header_class)
    # if not date:
    #     date_header_class = "brl-muhj-opening-date-right"
        # date = soup.find("p", class_=date_header_class)
    # if not date:
    #     date_header_class = "brl-muhj-addressee-and-opening-date"
        # date = soup.find('div', class_=date_header_class).find_all('p')[1]
    # date = date.text.replace("DATE: ", "").strip()
    if not soup.find('div', class_="brl-muhj-addressee-and-opening-date"):
        addressee = soup.find("p", class_="brl-muhj-addressee")
    else:
        addressee = soup.find('div', class_="brl-muhj-addressee-and-opening-date").p

    if not addressee:
        addressee = ""
    else:
        addressee = addressee.get_text(separator=" ").strip()
    paragraph_texts = list()
    for par in soup.find_all("p", class_="brl-muhj-paragraph"):
        text = par.text.strip()
        paragraph_texts.append(text)
    return date, addressee, paragraph_texts

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

def save_all_uhj_messages_as_txts():
    base_url = "https://www.bahai.org/library/authoritative-texts/the-universal-house-of-justice/messages/"
    messages = get_all_read_online_url_exts(base_url)
    for url_tail, summary in messages:
        url = base_url + url_tail
        date, addressee, paragraph_texts = get_message_data_from_html(url)
        with open('uhj/' + url_tail.split('/')[0] + '.txt', 'w') as f:
            f.write(date +'\n')
            f.write(addressee +'\n')
            f.write(summary +'\n')
            for par in paragraph_texts:
                f.write(par + '\n')


def convert_uhj_messages_txts_to_documents():
    docs = list()
    for folder, _, files in os.walk('data/uhj'):
        for file in files:
            fp = folder + '/' + file
            with open(fp, 'r', encoding='utf-8') as f:
                text = f.read().split("\n")
            date = text[0]
            addressee = text[1]
            summary = text[2].strip()
            contents = text[3:]
            print("Date: " + date)
            print("Addressee: " + addressee)
            print("Title: " + summary)
            print("Contents: " + '\n'.join(contents))

            metadata = {
                "author": "UHJ",
                "date": date,
                "addressee": addressee,
                "title": summary
            }

            for par in contents:
                chunk = '\n'.join([date, addressee, summary, par])
                doc = Document(page_content=chunk, metadata=metadata)
                docs.append(doc)
    return docs