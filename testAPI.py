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
import os
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm

from apiSettings import ApiSettings
import random
import re

import openai

import aiTest

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

settings = ApiSettings()

app = Flask(__name__)
CORS(app)

# One-time model init
model = SentenceTransformer('all-MiniLM-L6-v2')


def create_response(user_msg, max_tokens=200, temperature=0.7):
    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "User seeks book. Recognize intent, recommend three books with title, author, and link if known. Respond as JSON."},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    return response.choices[0].message.content


def parse_query(message):
    language = 'english'
    search_terms = []
    skip_indices = set()
    year_data = settings.YEAR_FILTER_WORDS[-1]

    message = re.sub(r'[^\w\s]', '', message).lower()
    words = message.split()

    for i, word in enumerate(words):
        if word in settings.LANGUAGE_CODES:
            language = word
            skip_indices.add(i)  # Don't include in search_terms

        if word in settings.YEAR_FILTER_WORDS:
            year_data = settings.YEAR_FILTER_WORDS[word]

        elif word in settings.NUM_RESULTS_WORDS:
            # Check neighboring digit
            if (i > 0 and words[i - 1].isdigit()):
                settings.num_books = int(words[i - 1])
                skip_indices.update({i, i - 1})
            elif (i < len(words) - 1 and words[i + 1].isdigit()):
                settings.num_books = int(words[i + 1])
                skip_indices.update({i, i + 1})
            settings.num_books = min(max(settings.num_books, 3), 30)

    search_terms = [
        word for i, word in enumerate(words)
        if i not in skip_indices and word not in settings.STOP_WORDS
    ]

    clean_query = ' '.join(search_terms)
    return clean_query, language, year_data


def is_popular(book):
    """Check if book meets minimum popularity standards"""
    if book.get('ratings_count', 0) < settings.min_ratings:
        return False
    if float(book.get('ratings_average', 0)) < settings.min_avg_rating:
        return False
    return True


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (norm(a) * norm(b))


def semantic_sort(books, message, year_data):
    if not books or not message:
        return books

    target_year, year_weight = year_data
    book_texts = [b.get('description') or b['title'] for b in books]

    # Generate embeddings
    query_embedding = model.encode(message, convert_to_tensor=False)
    book_embeddings = model.encode(book_texts, convert_to_tensor=False)

    scores = []
    for i, book in enumerate(books):
        # Semantic match (50%)
        semantic_score = np.dot(query_embedding, book_embeddings[i])

        # Popularity (weighted)
        popularity = np.log1p(book.get('ratings_count', 0)) * book.get('ratings_average', 0)
        pop_weight = settings.popularity_weight

        # Year closeness (weighted)
        book_year = int(book.get('year')) if book.get('year') and str(book.get('year')).isdigit() else None
        if book_year:
            year_score = 6 / (1 + 0.01 * abs(book_year - target_year))  # closer years get higher score
        else:
            year_score = 0  # no info

        total_score = (
            (1 - pop_weight - year_weight) * semantic_score +
            pop_weight * popularity +
            year_weight * year_score
        )

        scores.append(total_score)

    # Sort by score
    sorted_books = [book for _, book in sorted(
        zip(scores, books),
        key=lambda x: x[0],
        reverse=True
    )]

    return sorted_books


def format_book_data(doc):
    return {
        'key': doc.get('key'),
        'title': doc.get('title'),
        'author': ', '.join(doc.get('author_name', ['Unknown'])),
        'year': str(doc.get('first_publish_year', 'Unknown')),
        'pageCount': doc.get('number_of_pages_median', 'Unknown'),
        'subjects': doc.get('subject', [])[:5],
        'ratings_average': doc.get('ratings_average', 0),
        'ratings_count': doc.get('ratings_count', 0),
        'cover_id': doc.get('cover_i'),
        'description': '',
        'previewLink': ''
    }


def fetch_open_library_books(message):
    print(f"Processing message: {message}")
    topics, language, year_data = parse_query(message)
    print(f"Searching for books with terms: {topics}")

    print(f"Filtering for {language} language books")

    try:
        encoded_message = urllib.parse.quote(topics)
        language_code = settings.LANGUAGE_CODES.get(language, 'eng')
        url = (
            f"https://openlibrary.org/search.json?q={urllib.parse.quote(topics)}"
            f"&sort=rating"
            f"&limit={settings.initial_fetch_limit}"
            f"&language={language_code}"
            f"&fields=title,author_name,first_publish_year,number_of_pages_median,"
            f"subject,ratings_average,ratings_count,cover_i,key"
        )

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
                    description = generate_description(doc)

                book = format_book_data(doc)
                book['description'] = description
                # Provide a preview/search link
                book['previewLink'] = f"<a href='https://kcls.bibliocommons.com/v2/search?query={urllib.parse.quote(doc.get('title',''))}&searchType=smart' target='_blank'>Search in KCLS</a>"

                books.append(book)

            print(f"Processing complete. Found {len(books)} valid books")
            return books, topics, language, year_data
        else:
            print(f"API request failed with status code: {response.status_code}")
            return [], topics, language, year_data

    except requests.RequestException as e:
        print(f"Error fetching books: {e}")
        return [], topics, language, year_data


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
    author = book.get('author', '')
    lang_part = (language.capitalize() if language != 'english' else '')
    query = urllib.parse.quote(f"{title} {author} {lang_part}")
    return f"<a href='https://kcls.bibliocommons.com/v2/search?query={query}&searchType=smart' target='_blank'>Search in KCLS</a>"


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
    full_stars = round(rating)
    empty_stars = 5 - full_stars

    return (
        f"{'★' * full_stars}{'☆' * empty_stars} "
        f"{rating:.1f}/5 ({int(count):,} ratings)"
    )


def format_books_info(books):
    book_info = ""

    for book in books:
        cover_img = f"<img src='https://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg' class='book-cover'>" if book['cover_id'] else ""

        book_info += f"""
        <div class='book-container'>
            <div class='cover-container'>{cover_img}</div>
            <div class='book-details'>
                <div class='book-title'>{book['title']}</div>
                <div class='book-author'>By {book['author']}</div>
                <div class='book-published'>Published: {book.get('year','Unknown')}</div>
                <div class='book-rating'>{format_rating(book.get('ratings_average',0), book.get('ratings_count',0))}</div>
                <div class='description-container'>
                    <span class='description-trigger'>📖 Description</span>
                    <div class='description-popup'>{book.get('description','')}</div>
                </div>
                <div class='library-link'>{book.get('previewLink','')}</div>
            </div>
        </div>
        <hr class='book-divider'>
        """
    return book_info


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    books, topics, language, year_data = fetch_open_library_books(message)

    # Sort semantically and pick top results
    books = semantic_sort(books, message, year_data)
    top_books = books[:settings.num_books]

    for book in top_books:
        if book.get('key'):
            book['description'] = fetch_book_description(book['key']) or generate_description(book)
        book['previewLink'] = generate_link(book, language)

    response_message = format_message(top_books, topics, language) + f"<br>{format_books_info(top_books)}"
    return jsonify({"message": response_message})


# Run the Flask app if this is the main module
if __name__ == "__main__":
    app.run(debug=True)
