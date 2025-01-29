"""
Peter and Max  
Last updated 1/29/2025  
This script implements a Flask web API that provides a semantic search for books using Sentence Transformers.  
The API accepts a POST request with a search query and returns the top matching books based on semantic similarity.  
It uses the 'all-MiniLM-L6-v2' model from the Sentence Transformers library to encode both the book descriptions and the user query,  
and compares them using cosine similarity.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)
CORS(app)

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample book data (fake data)
books = [
    {"title": "Understanding AI", "description": "A comprehensive guide to artificial intelligence and its applications."},
    {"title": "Adventures in Space", "description": "A thrilling journey through the cosmos with astronauts."},
    {"title": "Mystery of the Lost Island", "description": "A gripping tale of adventure and mystery on a deserted island."},
    {"title": "Cooking 101", "description": "Learn the basics of cooking with easy and fun recipes."},
    {"title": "The Art of Data Science", "description": "A detailed exploration of data analysis and machine learning techniques."},
]

# Encode book descriptions into embeddings
book_descriptions = [book["description"] for book in books]
book_embeddings = model.encode(book_descriptions, convert_to_tensor=True)

@app.route('/api/search', methods=['POST'])
def search_books():
    try:
        # Get data from the incoming request
        data = request.get_json()
        query = data.get('query', '')  # Default empty string if no query provided
        top_k = data.get('top_k', 3)  # Default to top 3 results if top_k not specified

        # Encode the query into embedding
        query_embedding = model.encode(query, convert_to_tensor=True)

        # Compute cosine similarity between the query and book descriptions
        similarity_scores = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]

        # Get the top-k results based on similarity
        top_results = torch.topk(similarity_scores, k=min(top_k, len(books)))

        # Prepare the results to return in JSON format
        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            results.append({
                "title": books[idx]["title"],
                "description": books[idx]["description"],
                "score": float(score)
            })

        # Return the results as a JSON response
        return jsonify({"results": results})

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500

# Start the Flask web server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
