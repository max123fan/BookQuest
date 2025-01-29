from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

def fetch_open_library_books(message):
    print(f"Processing message: {message}")
    stop_words = {'a', 'an', 'the', 'i', 'want', 'book', 'that', 'has', 'with', 'about'}
    search_terms = ' '.join([word for word in message.lower().split() if word not in stop_words])
    print(f"Searching for books with terms: {search_terms}")
    
    try:
        encoded_message = urllib.parse.quote(search_terms)
        url = f"https://openlibrary.org/search.json?q={encoded_message}&limit=5&language=eng"
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
                    'previewLink': f"<a href='https://kcls.bibliocommons.com/v2/search?query={urllib.parse.quote(doc.get('title', ''))}&searchType=smart' target='_blank'>Search in KCLS</a>",
                    'publishedDate': str(doc.get('first_publish_year', 'Unknown')),
                    'pageCount': doc.get('number_of_pages_median', 'Unknown'),
                    'subjects': doc.get('subject', [])[:5],
                    'averageRating': doc.get('ratings_average', 'Not rated'),
                    'cover_id': doc.get('cover_i'),
                    'description': description  # Ensure description is included
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
        open_library_url = f"https://openlibrary.org{work_key}.json"
        response = requests.get(open_library_url)
        if response.status_code == 200:
            data = response.json()
            return data.get('description', {}).get('value', '') if isinstance(data.get('description'), dict) else data.get('description', '')
        return ''
    except:
        return ''

def format_books_info(books):
    book_info = ""
    for book in books:
        # Add cover image if available
        cover_img = ""
        if book['cover_id']:
            cover_img = f"<img src='https://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg' class='book-cover'>"
        
        # Add description hover element
        description_popup = f"""
        <div class='description-container'>
            <span class='description-trigger'>📖 Description</span>
            <div class='description-popup'>
                {book['description']}
            </div>
        </div>
        """
        
        book_info += f"""
        <div class='book-container'>
            <div class='cover-container'>{cover_img}</div>
            <div class='book-details'>
                <div class='book-title'>{book['title']}</div>
                <div class='book-author'>By {book['author']}</div>
                <div class='book-published'>Published: {book['publishedDate']}</div>
                {description_popup}
                <div class='library-link'>{book['previewLink']}</div>
            </div>
        </div>
        <hr class='book-divider'>
        """
    return book_info
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    print(f"Received message: {message}")
    books = fetch_open_library_books(message)
    
    response_message = f"Here are the results:<br>{format_books_info(books)}" if books else "Sorry, no books were found matching your query."
    return jsonify({"message": response_message})

def print_doc(doc):
    for element in doc:
        print(doc)

if __name__ == "__main__":
    app.run(debug=True)