<<<<<<< HEAD
BookQuest
Project Overview
BookQuest is an AI-powered chatbot integrated into a website that helps users find books in the KCLS library database based on their queries. The chatbot makes API calls to the Open Library API and retrieves a list of relevant books. It uses semantic search with text embeddings and cosine similarity as a comparsion metric find books that are most related to the goal of the user's query, and then uses query string paramaterization and minuplation to generate and retrive the corresponding links to the books in the KCLS database.

Features
Chatbot Interface w/ all-MiniLM-L6-v2: The chatbot accepts queries from users and provides an interactive interface for book recommendations.
Semantic Search: BookQuest uses advanced semantic search techniques to understand the meaning behind a user's query, providing a more accurate and relevant
response in search results compared to traditional keyword search techniques . Text Embeddings: The system transforms both user queries and book descriptions into numerical vectors (embeddings) to capture the semantic meaning of the text.
Cosine Similarity: The chatbot compares the user's query with book descriptions using the cosine similarity metric, which measures how similar two text vectors are in terms of their direction. This allows the chatbot to return the most semantically relevant books, even if they don't contain exact keyword matches.
Open Library Integration: BookQuest makes API calls to Open Library to retrieve a list of books based on the user's query.
KCLS Integration: The chatbot generates KCLS links for each book and provides users with the title, picture, description and other relevant info with query manipulation & parametrization
Technologies Used
Frontend: HTML, CSS, JavaScript (React.js for dynamic interactions)
Backend: Python (Flask or FastAPI for API calls and backend logic)
API Integration: Open Library API (for fetching book data)
Semantic Search: incorporated all-MiniLM-L6-v2, a Mini Language Model variant, for generating sentence embeddings.
Cosine Similarity: Used to compare the similarity between query vectors and book vectors.
KCLS Link Generation: URL construction to dynamically generate KCLS links.
=======
# BookQuest

## Project Overview

**BookQuest** is an AI-powered chatbot integrated into a website that helps users find books in the KCLS library database based on their queries. The chatbot makes API calls to the Open Library API and retrieves a list of relevant books. It uses semantic search  with text embeddings and cosine similarity as a comparsion metric find books that are most related to the goal of the user's query, and then uses query string paramaterization and minuplation to generate and retrive the corresponding links to the books in the KCLS database.

---

## Features

- **Chatbot Interface w/ all-MiniLM-L6-v2**: The chatbot accepts queries from users and provides an interactive interface for book recommendations.
- **Semantic Search**: BookQuest uses advanced semantic search techniques to understand the meaning behind a user's query, providing a more accurate and relevant
- response in search results compared to traditional keyword search techniques .
  **Text Embeddings**: The system transforms both user queries and book descriptions into numerical vectors (embeddings) to capture the semantic meaning of the text.
- **Cosine Similarity**: The chatbot compares the user's query with book descriptions using the cosine similarity metric, which measures how similar two text vectors are in terms of their direction. This allows the chatbot to return the most semantically relevant books, even if they don't contain exact keyword matches.
- **Open Library Integration**: BookQuest makes API calls to Open Library to retrieve a list of books based on the user's query.
- **KCLS Integration**: The chatbot generates KCLS links for each book and provides users with the title, picture, description and other relevant info with
  query manipulation & parametrization

---

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (React.js for dynamic interactions)
- **Backend**: Python (Flask or FastAPI for API calls and backend logic)
- **API Integration**: Open Library API (for fetching book data)
- **Semantic Search**: incorporated all-MiniLM-L6-v2, a Mini Language Model variant, for generating sentence embeddings.
- **Cosine Similarity**: Used to compare the similarity between query vectors and book vectors.
- **KCLS Link Generation**: URL construction to dynamically generate KCLS links.


---
 
>>>>>>> 25ddb2efe0db83d0b4f15500db4598ea4ba61580
