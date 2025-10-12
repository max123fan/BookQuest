from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib.parse


from apiSettings import ApiSettings
import random
import re


import aiTest
import json

settings = ApiSettings()

app = Flask(__name__)
CORS(app)

# In-memory messages store: { session_id: [ {role, content}, ... ] }
messages_store = {}

def get_openlibrary_doc(title, author):

    try:
        # Define all fields to match Exhibit A and more
        fields = (
            "key,title,author_name,first_publish_year,number_of_pages_median,"
            "ratings_average,ratings_count,cover_i"
        )
        # Construct URL with exact title and author
        url = (
            f"https://openlibrary.org/search.json?"
            f"title={urllib.parse.quote(title)}&author={urllib.parse.quote(author)}"
            f"&fields={fields}&limit=10"
        )
        # print(f"Request URL: {url}")  # Debug
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        total_found = data.get('numFound', 0)
        if total_found == 0:
            return settings.default_doc
        
        # Find the first doc with exact title and author match
        for doc in data.get('docs', []):
            if not doc.get('title'):
                continue
            if (doc.get('title').lower() == title.lower() and
                any(author.lower() in a.lower() for a in doc.get('author_name', []))):
                # print(f"Matched doc: {doc}")  # Debug
                return doc
        return settings.default_doc
    
    except requests.RequestException as e:
        return f'Error fetching data: {str(e)}'
    except Exception as e:
        return f'Error parsing data: {str(e)}'


def fetch_book_description(work_key):
    try:
        open_library_url = f"https://openlibrary.org{work_key}.json"
        response = requests.get(open_library_url)
        if response.status_code == 200:
            data = response.json()
            return data.get('description', {}).get('value', '') if isinstance(data.get('description'), dict) else data.get('description', '')
        return ''
    except:
        return ''
    
def generate_description(doc):
    """Generate fallback description"""
    desc = f"{doc.get('title')}. "
    if doc.get('author_name'):
        desc += f"Written by {', '.join(doc['author_name'])}. "
    if doc.get('subject'):
        desc += f"Subjects: {', '.join(doc['subject'][:5])}."
    return desc

def generate_link(book, language):
    title = book['title']
    return f"<a href='https://kcls.bibliocommons.com/v2/search?query={urllib.parse.quote(title + ' ' + book['author'] + ' ' + (language.capitalize() if language != 'english' else ''))}&searchType=smart' target='_blank'>Search in KCLS</a>"


def format_message(books, topics, language):
    if not books:
        return "Sorry, no books were found matching your query."

    
    lang_phrase = "."
    if language != "english":
        lang_phrase = f", available in {language.capitalize()}."
    
    responses = [f"Try these {len(books)} books for your next read",
                 f"{len(books)} results found",
                 f"You may enjoy these {len(books)} books",
                 f"I recommend these {len(books)} books for you"
                 ]
    return random.choice(responses) + lang_phrase

def format_rating(average, count):
    if average == 'Not rated':
        return "Not rated"
    
    rating = float(average)
    full_stars = round(rating)  # Recommended: rounding for fairness
    empty_stars = 5 - full_stars
    
    return (
        f"{'★' * full_stars}{'☆' * empty_stars} "
        f"{rating:.1f}/5 ({int(count):,} ratings)"
    )

def get_availability_text(availability):
    if availability:
        return "Available"
    return "All copies in use"


def format_books_info(books, template_path='book_template.html'):
    with open(template_path, 'r', encoding='utf-8') as f:
        book_template = f.read()

    book_info = ""

    for book in books:
        cover_img = ""
        if book['cover_id']:
            cover_img = f"<img src='https://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg' class='book-cover'>"

        rating = format_rating(book['ratings_average'], book['ratings_count'])
        availability_text = get_availability_text(book['availability'])

        book_info += book_template.format(
            cover_img=cover_img,
            title=book['title'],
            author=book['author'],
            year=book['year'],
            rating=rating,
            description=book['description'],
            link=book['link'],
            media_type = book['media_type'],
            availability = str(book['availability']),
            availability_text=availability_text
        )

    return book_info

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # support session-based history
    session_id = data.get('session_id', 'default')
    message = data.get('message', '')
    
    # initialize messages for session if missing
    messages = messages_store.get(session_id, [{"role": "system", "content": "You are an assistant that helps find books."}])
    # append user message to history
    messages.append({"role": "user", "content": message})

    # Call the model but only send the last two turns to limit tokens
    system_msg = messages[0] if messages and messages[0].get('role') == 'system' else None
    last_two = messages[-2:]
    send_parts = []
    if system_msg:
        send_parts.append(f"SYSTEM: {system_msg.get('content','')}")
    for m in last_two:
        role = m.get('role', 'user').upper()
        send_parts.append(f"{role}: {m.get('content','')}")
    composite_prompt = "\n".join(send_parts)

    # aiTest.create_response expects a single string prompt
    books = aiTest.create_response(composite_prompt)
    # store assistant reply in session history (store the JSON string)
    assistant_text = json.dumps(books)
    messages.append({"role": "assistant", "content": assistant_text})
    messages_store[session_id] = messages
    print(books)

    #books = [{'title': 'Dune', 'subtitle': 'The epic saga of the desert planet Arrakis', 'author': 'Frank Herbert', 'media_type': 'book'}, {'title': 'Hyperion', 'subtitle': '', 'author': 'Dan Simmons', 'media_type': 'book'}]

    for book in books:
        print()
        aiTest.update_kcls_availability(book)

    books = [book for book in books if book.get('exist', True)]

    for book in books:
        author = book['author']
        title = book['title']
        ol_doc = get_openlibrary_doc(title, author)
        print(ol_doc)
        if ol_doc:
            book['key'] = ol_doc.get('key')
            book['cover_id'] = ol_doc.get('cover_i')
            book['ratings_average'] = ol_doc.get('ratings_average', 0)
            book['ratings_count'] = ol_doc.get('ratings_count', 0)
            book['description'] = fetch_book_description(ol_doc.get('key')) or generate_description(ol_doc)
            book['year'] = str(ol_doc.get('first_publish_year', 'Unknown')[0] if isinstance(ol_doc.get('first_publish_year'), tuple) else ol_doc.get('first_publish_year', 'Unknown'))
        

    
    response_message = f"<br>{format_books_info(books)}"
    return jsonify({"message": response_message, "session_id": session_id, "messages": messages})


if __name__ == "__main__":
    app.run(debug=True)