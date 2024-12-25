from sentence_transformers import SentenceTransformer, util
import torch

#Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')  # A lightweight, efficient model for semantic similarity.

# Sample book data (fake data)
books = [
    {"title": "Understanding AI", "description": "A comprehensive guide to artificial intelligence and its applications."},
    {"title": "Adventures in Space", "description": "A thrilling journey through the cosmos with astronauts."},
    {"title": "Mystery of the Lost Island", "description": "A gripping tale of adventure and mystery on a deserted island."},
    {"title": "Cooking 101", "description": "Learn the basics of cooking with easy and fun recipes."},
    {"title": "The Art of Data Science", "description": "A detailed exploration of data analysis and machine learning techniques."},
]

#  Encode book descriptions into embeddings
book_descriptions = [book["description"] for book in books]
book_embeddings = model.encode(book_descriptions, convert_to_tensor=True)

# Semantic search function
def search_books(query, top_k=3):

    # Encode the query
    query_embedding = model.encode(query, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]

    # Get top-k scores and corresponding book indices
    top_results = torch.topk(similarity_scores, k=top_k)

    # Return the top matching books
    results = []
    for score, idx in zip(top_results.values, top_results.indices):
        results.append({
            "title": books[idx]["title"],
            "score": score.item()
        })
    return results

 
if __name__ == "__main__":
    user_query = "Basics of artificial intelligence and machine learning"
    results = search_books(user_query, top_k=3)

    print("Search Results:")
    for result in results:
        print(f"Title: {result['title']}, Score: {result['score']:.4f}")
