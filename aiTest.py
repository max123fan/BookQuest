#supports mutimedia/multi-language

import openai
import requests
import json
import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def create_response(user_msg, max_tokens=500):
    system_prompt = """
        You are an assistant that generates book recommendations based on user input.
        Default to 5 books unless user says otherwise.
        Output a JSON array of books, no extra text.

        Each book is an object with
        "title" (string, super concise title, disregard any sub titles),
        "author" (string, minimally concise),
        "media_type" ("book" by default, or "audiobook", "ebook" if specified).
        """

    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=max_tokens
    )

    return json.loads(response.choices[0].message.content)

def update_kcls_availability(book, timeout=4):
    title = book.get('title', '').lower()
    subtitle = book.get('subtitle', '').lower()
    author_lastname = book.get('author', '').strip().split()[-1].lower()
    media_type = book.get('media_type', '').lower()

    media_type_code_key = {"book": "bk",
                           "ebook": "ebook",
                           "audiobook": "CS OR BOOK_CD OR AB OR PLAYAWAY_AUDIOBOOK",
                           }
    
    media_type_code = media_type_code_key.get(media_type, "bk")

    # build the raw query and percent-encode it to safely handle special characters
    raw_query = f"(title:({title}) AND contributor:({author_lastname})) formatcode:({media_type_code})"
    query = quote_plus(raw_query, safe='')
    url = f"https://kcls.bibliocommons.com/v2/search?custom_edit=false&query={query}&searchType=bl&suppress=true"
    
    book['availability'] = False
    book['link'] = url
    book['exist'] = True

    print(url)

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return False, None

    soup = BeautifulSoup(resp.content, 'lxml')
    title_lower = title.lower().strip()

    info_block = soup.find('li', class_='row cp-search-result-item')
    
    # Iterate cp-search-result-item siblings and only check manifestation items inside a matching info block
    while info_block:
        title_block = info_block.select_one('.title-content, span.title-content, .cp-title .title-content, h2 .title-content')
        if title_block and title_block.get_text(strip=True):
            info_title = title_block.get_text(strip=True).strip()
            print(info_title, title_lower)
            if info_title.lower() in title_lower or title_lower in info_title.lower():
                book['title'] = info_title
                for manifestation_block in info_block.find_all('div', class_='manifestation-item cp-manifestation-list-item row'):
                    availability_block = manifestation_block.find('div', class_='manifestation-item-availability-block-wrap')
                    if availability_block:
                        status_span = availability_block.find('span', class_='cp-availability-status')

                        if status_span:
                            status_text = status_span.get_text(strip=True).lower()
                            is_available = ("available" in status_text) and ("not" not in status_text)

                            if is_available:
                                book['availability'] = True

                            link_tag = manifestation_block.find('a', class_='manifestation-item-link')
                            if link_tag and link_tag.has_attr('href'):
                                full_link = "https://kcls.bibliocommons.com" + link_tag['href']
                                book['link'] = full_link

                            book['exist'] = True
                            return
                # title matched but no manifestation inside this info block matched — continue to next info block
        # advance to next top-level search result item
        print("No matching manifestation found in this info block, checking next sibling.", title_lower)
        info_block = info_block.find_next_sibling('div', class_='cp-search-result-item')

    # If none matched
    book['exist'] = False


#books = [{'title': 'The Dark Forest', 'subtitle': '', 'author': 'Liu Cixin', 'media_type': 'ebook'}]
#books = [{'title': 'The 13-story Treehouse', 'subtitle': '', 'author': 'Andy Griffiths', 'media_type': 'audiobook'}]
#books =[{'title': 'Percy Jackson & The Olympians: The Lightning Thief', 'author': 'Rick Riordan', 'media_type': 'ebook'}]

# print(books, "\n")

# for book in books:
#     print("Title:", book['title'])
#     update_kcls_availability(book)
#     print(book['availability'], book['link'])
