"""
 Peter and Max
 Last updated 1/29/2025
 Description: This Flask application accepts a POST request with a message containing book-related search terms. 
 It queries the Open Library API to find books matching the message, retrieves book information (including title, author, description, and cover), 
 and formats the results to display the book details in a user-friendly HTML format.
 The API then returns a response containing the formatted book information or an error message if no books are found.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

# Function to fetch books from Open Library based on search terms
def fetch_open_library_books(message):
    print(f"Processing message: {message}")
    
    # Define stop words that should be excluded from the search
    stop_words = {'a', 'an', 'the', 'i', 'want', 'book', 'that', 'has', 'with', 'about'}
    
    # Remove stop words from the message and prepare the search terms
    search_terms = ' '.join([word for word in message.lower().split() if word not in stop_words])
    print(f"Searching for books with terms: {search_terms}")
    
    try:
        # URL-encode the search terms for the API query
        encoded_message = urllib.parse.quote(search_terms)
        
        # Define the Open Library API search endpoint with parameters
        url = f"https://openlibrary.org/search.json?q={encoded_message}&limit=5&language=eng"
        
        # Send GET request to Open Library API
        response = requests.get(url)
        books = []
        
        if response.status_code == 200:
            # If response is successful, parse JSON data
            data = response.json()
            total_found = data.get('numFound', 0)
            print(f"Found {total_found} total books in response")
            
            # Loop through each book document in the response
            for doc in data.get('docs', []):
                # Skip books without a title
                if not doc.get('title'):
                    continue
                
                # Get the work key for fetching detailed information about the book
                work_key = doc.get('key', '')
                
                # Fetch book description if available
                description = fetch_book_description(work_key) if work_key else ''
                
                # If no description, build a basic description using available information
                if not description:
                    description = f"{doc.get('title')}. "
                    if doc.get('author_name'):
                        description += f"Written by {', '.join(doc['author_name'])}. "
                    if doc.get('subject'):
                        description += f"Subjects: {', '.join(doc['subject'][:5])}."
                
                # Append the book information to the list of books
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
            # If API request fails, log error and return empty list
            print(f"API request failed with status code: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        # Handle exceptions in case of network or API request errors
        print(f"Error fetching books: {e}")
        return []

# Function to fetch detailed book description from Open Library based on work key
def fetch_book_description(work_key):
    try:
        # Construct the URL to fetch book details
        open_library_url = f"https://openlibrary.org{work_key}.json"
        
        # Send GET request to Open Library for book details
        response = requests.get(open_library_url)
        
        if response.status_code == 200:
            data = response.json()
            # Return the description if it is present in the response
            return data.get('description', {}).get('value', '') if isinstance(data.get('description'), dict) else data.get('description', '')
        return ''
    except:
        # If there's an error, return an empty string
        return ''

# Function to format and generate HTML to display book information
def format_books_info(books):
    book_info = ""
    for book in books:
        # Add cover image if available
        cover_img = ""
        if book['cover_id']:
            cover_img = f"<img src='https://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg' class='book-cover'>"
        
        # Add description hover element for better user experience
        description_popup = f"""
        <div class='description-container'>
            <span class='description-trigger'>📖 Description</span>
            <div class='description-popup'>
                {book['description']}
            </div>
        </div>
        """
        
        # Generate the HTML for each book, including title, author, description, and cover image
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

# Flask route to handle the '/chat' POST request
@app.route('/chat', methods=['POST'])
def chat():
    # Get the message from the POST request data
    data = request.get_json()
    message = data.get('message', '')
    print(f"Received message: {message}")
    
    # Fetch books based on the message
    books = fetch_open_library_books(message)
    
    # Format the results into a user-friendly HTML format
    response_message = f"Here are the results:<br>{format_books_info(books)}" if books else "Sorry, no books were found matching your query."
    
    # Return the formatted book information or error message as a JSON response
    return jsonify({"message": response_message})

# Debugging function to print the document data (currently unused)
def print_doc(doc):
    for element in doc:
        print(doc)

# Run the Flask app if this is the main module
if __name__ == "__main__":
    app.run(debug=True)
