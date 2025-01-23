from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from sentence_transformers import SentenceTransformer, util
import requests
import sys
import time
import urllib.parse

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def fetch_open_library_books(message):
    print(f"Processing message: {message}")
    stop_words = {'a', 'an', 'the', 'i', 'want', 'book', 'that', 'has', 'with', 'about'}
    search_terms = ' '.join([word for word in message.lower().split() if word not in stop_words])
    
    print(f"Searching for books with terms: {search_terms}")
    
    try:
        encoded_message = urllib.parse.quote(search_terms)
        url = f"https://openlibrary.org/search.json?q={encoded_message}&limit=20&language=eng"
        
        response = requests.get(url)
        books = []
        
        if response.status_code == 200:
            data = response.json()
            total_found = data.get('numFound', 0)
            print(f"Found {total_found} total books in response")
            
            for doc in data.get('docs', []):
                if not doc.get('title'):
                    continue
                work_key = doc.get('key', '')
                description = fetch_book_description(work_key) if work_key else ''
                if not description:
                    description = f"{doc.get('title')}. "
                    if doc.get('author_name'):
                        description += f"Written by {', '.join(doc['author_name'])}. "
                    if doc.get('subject'):
                        description += f"Subjects: {', '.join(doc['subject'][:5])}."
                
                books.append({
                    'title': doc.get('title'),
                    'author': ', '.join(doc.get('author_name', ['Unknown'])),
                    'description': description,
                    'previewLink': f"https://openlibrary.org{work_key}",
                    'publishedDate': str(doc.get('first_publish_year', 'Unknown')),
                    'pageCount': doc.get('number_of_pages_median', 'Unknown'),
                    'subjects': doc.get('subject', [])[:5],
                    'averageRating': doc.get('ratings_average', 'Not rated'),
                    'cover_id': doc.get('cover_i')
                })
            
            print(f"Processing complete. Found {len(books)} valid books")
            return books
        else:
            print(f"API request failed with status code: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        print(f"Error fetching books: {e}")
        return []

def fetch_book_description(work_key):
    try:
        url = f"https://openlibrary.org{work_key}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('description', {}).get('value', '') if isinstance(data.get('description'), dict) else data.get('description', '')
        return ''
    except:
        return ''

def format_books_info(books):
    # Create a formatted string with line breaks for each book
    book_info = ""
    for book in books:
        book_info += f"Title: {book['title']}<br>"
        book_info += f"Author: {book['author']}<br>"
        book_info += f"Description: {book['description']}<br>"
        book_info += f"Link: {book['previewLink']}<br>"
        book_info += f"Page Count: {book['pageCount']}<br>"
        book_info += f"Average Rating: {book['averageRating']}<br>"
        book_info += f"<hr>"
    return book_info


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()  # Get the data from the frontend
    message = data.get('message', '')  # Extract the message from the received JSON
    print(f"Received message: {message}")

    # Process the query with Open Library API or your custom logic
    books = fetch_open_library_books(message)

    if books:
        # Format the response properly for readability
        formatted_books_info = format_books_info(books)
        response_message = f"Here are the results:\n{formatted_books_info}"
    else:
        response_message = "Sorry, no books found matching your query."

    return jsonify({"message": response_message})

if __name__ == "__main__":
    app.run(debug=True)
