from sentence_transformers import SentenceTransformer, util
import requests
import sys
import time
import urllib.parse

def load_model():
    print("Loading AI model...")
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

def fetch_open_library_books(query):
    print(f"Processing query: {query}")
    
    # Process natural language query into search terms
    stop_words = {'a', 'an', 'the', 'i', 'want', 'book', 'that', 'has', 'with', 'about'}
    search_terms = ' '.join([word for word in query.lower().split() 
                           if word not in stop_words])
    
    print(f"Searching for books with terms: {search_terms}")
    
    try:
        # Encode query for URL
        encoded_query = urllib.parse.quote(search_terms)
        url = f"https://openlibrary.org/search.json?q={encoded_query}&limit=20&language=eng"
        
        response = requests.get(url)
        books = []
        
        if response.status_code == 200:
            data = response.json()
            total_found = data.get('numFound', 0)
            print(f"Found {total_found} total books in response")
            
            for doc in data.get('docs', []):
                # Skip books without titles
                if not doc.get('title'):
                    continue
                
                # Get book description from the works API
                work_key = doc.get('key', '')
                description = fetch_book_description(work_key) if work_key else ''
                
                # If no description available, create one from metadata
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
    """Fetch book description from Open Library Works API"""
    try:
        url = f"https://openlibrary.org{work_key}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('description', {}).get('value', '') if isinstance(data.get('description'), dict) else data.get('description', '')
        return ''
    except:
        return ''

def semantic_search(model, query, books, top_k=5):
    try:
        if not books:
            return []

        print("Analyzing books for best matches...")
        
        # Combine title, author, and description for better matching
        book_contents = [
            f"Title: {book['title']}. Author: {book['author']}. "
            f"Description: {book['description']}"
            + (f" Subjects: {', '.join(book['subjects'])}." if book['subjects'] else "")
            for book in books
        ]
        
        # Create embeddings
        query_embedding = model.encode(query, convert_to_tensor=True)
        book_embeddings = model.encode(book_contents, convert_to_tensor=True)
        
        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]
        
        # Get top results
        top_results = similarities.argsort(descending=True)[:top_k]
        recommended_books = []
        
        for idx in top_results:
            book = books[idx]
            similarity_score = float(similarities[idx]) * 100
            book['similarity_score'] = similarity_score
            recommended_books.append(book)
            
        return recommended_books
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []

def display_book(book, index):
    similarity = book.get('similarity_score', 0)
    print(f"\n=== Book {index + 1} (Match: {similarity:.1f}%) ===")
    print(f"Title: {book['title']}")
    print(f"Author(s): {book['author']}")
    print(f"Published: {book['publishedDate']}")
    print(f"Pages: {book['pageCount']}")
    print(f"Rating: {book['averageRating']}")
    if book.get('subjects'):
        print(f"Subjects: {', '.join(book['subjects'])}")
    print(f"Preview Link: {book['previewLink']}")
    if book.get('cover_id'):
        print(f"Cover Image: https://covers.openlibrary.org/b/id/{book['cover_id']}-L.jpg")
    print("\nDescription:")
    
    # Print description with word wrap
    words = book['description'].split()
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= 80:
            current_line += word + " "
        else:
            print(current_line)
            current_line = word + " "
    if current_line:
        print(current_line)
    print("=" * 80)

def generate_kcls_links(recommended_books):
    print("\nKCLS Search Links for Recommended Books:\n")
    kcls_base_url = "https://kcls.bibliocommons.com/v2/search?query="
    for i, book in enumerate(recommended_books):
        title = urllib.parse.quote(book['title'])
        author = urllib.parse.quote(book['author'])
        kcls_link = f"{kcls_base_url}{title}+{author}&searchType=smart"
        print(f"Book {i + 1}: {book['title']} by {book['author']}")
        print(f"KCLS Link: {kcls_link}\n")

def main():
    print("\n=== AI Book Recommender (Open Library Edition) ===\n")
    print("This system understands natural language! Try queries like:")
    print("- I want a book about dragons and magic")
    print("- Show me books about space exploration and aliens")
    print("- Find me romantic comedies set in New York")
    print("\nType 'quit' to exit.\n")
    
    # Load the AI model
    model = load_model()
    
    while True:
        # Get user input
        query = input("\nWhat kind of book are you looking for?: ").strip()
        
        if not query:
            print("Please enter a search term.")
            continue
        
        if query.lower() == 'quit':
            print("\nThank you for using AI Book Recommender!")
            break
            
        # Show loading message
        print("\nSearching for books...\n")
        
        # Get books from Open Library API
        books = fetch_open_library_books(query)
        
        if not books:
            print("No books found. Please try a different search term.")
            continue
            
        # Use the original query for semantic search to maintain context
        recommended_books = semantic_search(model, query, books)
        
        if not recommended_books:
            print("Could not find any matching books. Please try a different search term.")
            continue
            
        # Display results
        print(f"\nFound {len(recommended_books)} recommended books that match your interests:\n")
        for i, book in enumerate(recommended_books):
            display_book(book, i)
        
        # Generate and display KCLS links
        generate_kcls_links(recommended_books)
            
        print("\nWould you like to search for more books?\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nThank you for using AI Book Recommender!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please try again or check your internet connection.")
