from bs4 import BeautifulSoup
from typing import Dict


def adj_handler(soup: BeautifulSoup) -> Dict:
    addressee = soup.find('p', class_="hb bd ob vd").text.strip()
    date = soup.find_all('p', class_='vd')[-1].text.strip()

    texts = {
        "addressee": addressee,
        "date": date,
        "contents": list()
    }

    #TODO Get categories and subcategories from table of contents
    for tree in soup.find_all('p')[3:-3]:
        texts["contents"].append(tree.text.strip())

    # for tree in soup.find_all('p', class_=None)[:-1]:
    #     paragraphs.append(tree.text.strip())

    # for tree in soup.find_all('p', class_="xc"):
    #     paragraphs.append(tree.text.strip())
        
    return texts

def ba_handler(soup: BeautifulSoup) -> Dict:
    letters = list()
    # title = soup.find('h1').contents[-1]
    section_title = ' '.join([tree.text.strip() for tree in soup.find_all('h2')][1:]) # Letters from Shoghi Effendi Guardian of the Bahá’í Cause January 21, 1922–July 17, 1932
    for letter_soup in soup.find_all('div', class_="cd xc"):
        letter = dict()
        letter["contents"] = list()
        letter_contents = letter_soup.find_all('p')
        # if len([paragraph for paragraph in letter_contents if paragraph.attrs == {'class': ['c', 'kb']}]) > 0:
        #     letter_has_section_headers = True
        # else:
        #     letter_has_section_headers = False
        subsection_header = ""
        for paragraph in letter_contents:
            if paragraph.attrs == {"class": ['c', 'cd', 'l', 'vb']}:
                letter["letter_title"] = paragraph.text.strip()
                continue
            elif paragraph.attrs == {"class": ['fd']}:
                letter["addressee"] = paragraph.text.strip()
                continue
            elif paragraph.attrs == {"class": ['ed']}:
                addressee_backup = paragraph.text.strip()
                continue
            elif paragraph.attrs == {"class": ['c', 'kb']}:
                # different_section_header = prev_section_header == section_header
                # if different_section_header:
                    # section_idx += 1
                subsection_header = paragraph.text.strip()
                letter["contents"].append({"subsection": subsection_header, "contents": list()})
                continue
            elif paragraph.attrs == {}:
                paragraph_content = paragraph.text.strip()
            if not letter.get("addressee", None) and addressee_backup != "":
                letter["addressee"] = addressee_backup
            # letter_info = '\n'.join([letter_title, addressee])
            # if letter_has_section_headers and section_header != "":
                # paragraph_content = '\n'.join([section_header, paragraph_content])
                # paragraphs.append('\n'.join([letter_title, addressee, section_header, paragraph_content]))
            # else:
            if subsection_header != "":
                for i in range(len(letter["contents"])):
                    if type(letter["contents"][i]) == dict:
                        if subsection_header == letter["contents"][i].get("subsection", None):
                            letter["contents"][i]["contents"].append(paragraph_content)
                            break
            else:
                letter["contents"].append(paragraph_content)
        letters.append(letter)

    letters = {
        "section_title": section_title,
        "contents": letters
    }
        
    return letters

def cf_handler(soup: BeautifulSoup) -> Dict:
    letters = list()
    addressee = soup.find('p', class_='j').text.strip()
    for child_soup in soup.find_all('div', class_="wc bd ub"):
        letter_soup = child_soup.parent
        letter = dict()
        letter["contents"] = list()
        letter_contents = letter_soup.find_all('p')
        subsection_header = ""
        for paragraph in letter_contents:
            if paragraph.attrs == {"class": ["c"]}:
                letter["date"] = paragraph.text.strip()
                continue
            elif paragraph.attrs == {"class": ["c", "l"]}:
                letter["letter_title"] = paragraph.text.strip()
                continue
            elif paragraph.attrs == {"class": ['c', 'kb']}:
                subsection_header = paragraph.text.strip()
                letter["contents"].append({"subsection": subsection_header, "contents": list()})
                continue
            elif paragraph.attrs == {}:
                paragraph_content = paragraph.text.strip()
            if subsection_header != "":
                for i in range(len(letter["contents"])):
                    if type(letter["contents"][i]) == dict:
                        if subsection_header == letter["contents"][i].get("subsection", None):
                            letter["contents"][i]["contents"].append(paragraph_content)
                            break
            else:
                letter["contents"].append(paragraph_content)
        letters.append(letter)
    #TODO Consider adding the "In Memoriam section"
    letters = {
        "addressee": addressee,
        "contents": letters
    }
        
    return letters

def gpb_handler(soup: BeautifulSoup) -> Dict:
    sections = list()
    # Foreward
    foreward_soup = soup.find("p", class_="c l bd ob").parent
    foreward_section = dict()
    foreward_section["contents"] = list()
    for par in foreward_soup.find_all("p"):
        if par.attrs == {"class": ["c", "l", "bd", "ob"]}:
            foreward_section["section_title"] = par.text.strip()
            continue
        elif par.attrs == {} or par.attrs == {"class": ["vd"]}:
            paragraph_content = par.text.strip()
        foreward_section["contents"].append(paragraph_content)

    sections.append(foreward_section)

    # Main content
    for section_header_html in soup.find_all("div", class_="hc"):
        section = dict()
        section["contents"] = list()
        
        section_html_soup = section_header_html.parent
        section["section_title"] = section_html_soup.find("div", class_="hc").text.strip().replace("  ", " ")
        for div in section_html_soup.find_all("div"):
            chapter = dict()
            chapter["contents"] = list()
            if div.attrs == {"class": ["bd", "ub"]}:
                chapter["title"] = div.text.strip()
                continue
            elif div.attrs == {}:
                for par in div.find_all("p"):
                    chapter["contents"].append(par)
            section["contents"].append(chapter)

    return {"contents": sections}

def pdc_handler(soup: BeautifulSoup) -> Dict:
    sections = list()
    for div in soup.find_all("div", class_="bd"):
        section = dict()
        section["contents"] = list()
        section["section_title"] = div.find("p", class_="bd c l ub").text.strip()
        for par in div.find_all("p"):
            if par.attrs in [{"class": ["bd"]}, {}]:
                section["contents"].append(par.text.strip())
        sections.append(section)
    # TODO Exception for "Humiliation Immediate and Complete"

    return {
        "addressee": soup.find("p", class_="vd wc").text.strip(),
        "contents": sections,
        "date": "March 28, 1941"
    }

def tdh_handler(soup: BeautifulSoup) -> Dict:
    sections = list()
    for section_header_html in soup.find_all("div", class_="bd ub wc"):
        section = dict()
        section["contents"] = list()
        # section["section_number"] = section_header_html.find("p", class_="c bd q").text.replace("–", "").strip()
        section["section_title"] = section_header_html.find("p", class_="c l").text.strip()

        section_html_soup = section_header_html.parent
        for par in section_html_soup.find_all("p"):
            if par.attrs == {"class": ["c"]}:
                section["date"] = par.text.strip()
            elif par.attrs in [{"class": ["vd"]}, {}]:
                section["contents"].append(par.text.strip())
        sections.append(section)

    return {
        "contents": sections
    }

def wob_handler(soup: BeautifulSoup) -> Dict:
    sections = list()
    for section_header_html in soup.find_all("p", class_="c bd l"):
        section = dict()
        section["contents"] = list()
        
        section_html_soup = section_header_html.parent
        subsection_header = ""
        for par in section_html_soup.find_all("p"):
            if par.attrs == {"class": ["ed"]}:
                section["addressee"] = par.text.strip()
                continue
            elif par.attrs == {"class": ["c", "bd", "l"]}:
                section["section_title"] = par.text.strip()
                continue
            elif par.attrs == {"class": ["vd"]} and len(par.text.strip().split(" ")) <= 3:
                section["date"] = par.text.strip()
                continue
            elif par.attrs in [{"class": ["dd"]}, {"class": ["ub"]}, {"class": ["zb", "cc"]}]:
                continue
            elif par.attrs == {"class": ["c", "kb"]}:
                subsection_header = par.text.strip()
                section["contents"].append({"subsection": subsection_header, "contents": list()})
                continue
            elif par.attrs == {} or (par.attrs == {"class": ["vd"]} and len(par.text.strip().split(" ")) > 3):
                par_content = par.text.strip()
            else:
                continue
            if subsection_header != "":
                for i in range(len(section["contents"])):
                    if type(section["contents"][i]) == dict:
                        if subsection_header == section["contents"][i].get("subsection", None):
                            section["contents"][i]["contents"].append(par_content)
                            break
            else:
                section["contents"].append(par_content)
        sections.append(section)
    for div in soup.find_all("div", class_="hc"):
        if div.text.strip() == "The Dispensation of Bahá’u’lláh":
            big_div = div.parent.parent
            section = dict()
            section["contents"] = list()
            section["addressee"] = big_div.find("p", class_="ed").text.strip()
            section["section_title"] = big_div.find("h2", class_="c g").text.strip()
            for header in big_div.find_all("h2", class_="c g")[1:]: # First entry is Title header, so skip
                subsection_header = header.text.strip()
                section["contents"].append({"subsection": subsection_header, "contents": list()})
                for par in header.parent.parent.find_all("p"):
                    if par.attrs in [{"class": ["dd"]}, {"class": ["ub"]}, {"class": ["zb", "cc"]}, {"class": ["ed"]}]:
                        continue
                    elif par.attrs in [{"class": ["wc"]}, {}] or (par.attrs == {"class": ["vd"]} and len(par.text.strip().split(" ")) > 3):
                        par_content = par.text.strip()
                    else:
                        continue
                    for i in range(len(section["contents"])):
                        if type(section["contents"][i]) == dict:
                            if subsection_header == section["contents"][i].get("subsection", None):
                                section["contents"][i]["contents"].append(par_content)
            sections.append(section)
    return {
        "contents": sections
    }

handlers = {
    "The Advent of Divine Justice": adj_handler,
    "Bahá’í Administration": ba_handler,
    "Citadel of Faith": cf_handler,
    "God Passes By": gpb_handler,
    "The Promised Day Is Come": pdc_handler,
    "This Decisive Hour": tdh_handler,
    "The World Order of Bahá’u’lláh": wob_handler
}
