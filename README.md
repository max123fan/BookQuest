# BookQuest

## Project Overview

**BookQuest** is an AI-powered chatbot integrated into a website that helps users find books based on their queries. By making API calls to the Open Library API, the chatbot retrieves a list of relevant books and generates KCLS (King County Library System) links for each book. **BookQuest** goes beyond simple keyword matching by using **semantic search** techniques, **text embeddings**, and the **cosine similarity** metric to find books that truly match the intent of the user's query, offering more relevant and personalized results.

---

## Features

- **AI-Powered Chatbot Interface**: The chatbot accepts natural language queries from users and provides an interactive interface for book recommendations.
- **Semantic Search**: BookQuest uses advanced semantic search techniques to understand the meaning behind a user's query, improving accuracy and relevance in search results.
- **Text Embeddings**: The system transforms both user queries and book descriptions into numerical vectors (embeddings) using techniques like **TF-IDF** or **BERT** to capture the semantic meaning of the text.
- **Cosine Similarity**: The chatbot compares the user's query with book descriptions using the cosine similarity metric, which measures how similar two text vectors are in terms of their direction. This allows the chatbot to return the most semantically relevant books, even if they don't contain exact keyword matches.
- **Open Library Integration**: BookQuest makes API calls to Open Library to retrieve a list of books based on the user's query.
- **KCLS Integration**: Dynamically generates KCLS links for each book, providing users with easy access to their local library system.
- **Query Manipulation & Parametrization**: The chatbot refines and optimizes user queries before making API calls to ensure better book matches.

---

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (React.js for dynamic interactions)
- **Backend**: Python (Flask or FastAPI for API calls and backend logic)
- **API Integration**: Open Library API (for fetching book data)
- **Semantic Search**: Natural Language Processing (NLP) techniques using **TF-IDF**, **BERT**, or similar embedding models.
- **Cosine Similarity**: Used to compare the similarity between query vectors and book vectors.
- **KCLS Link Generation**: URL construction to dynamically generate KCLS links.
- **Hosting**: Heroku (for deployment)

---

## How Semantic Search Works

### 1. **Text Embeddings**

When a user enters a query, the chatbot converts the query into a vector representation using **text embeddings**. Text embeddings are numerical representations of text that capture the semantic meaning of words and phrases. Techniques like **TF-IDF** or **BERT** (Bidirectional Encoder Representations from Transformers) are used to convert both user queries and book descriptions into these high-dimensional vectors.

### 2. **Cosine Similarity**

Once the query and book descriptions are transformed into embeddings, **cosine similarity** is applied to measure the similarity between the query vector and each book vector. Cosine similarity compares the angle between two vectors, where a smaller angle (i.e., a higher cosine similarity score) indicates greater similarity. This allows the chatbot to return the most relevant books, even when the exact keywords in the query don't match those in the book descriptions.

### 3. **Query Refinement**

Before making the API call to Open Library, the chatbot refines the user's query to remove noise words or adjust phrasing to improve the likelihood of a match.

### 4. **Book Retrieval**

After determining the most relevant books based on semantic similarity, the chatbot retrieves a list of books from Open Library and provides KCLS links for easy access.

---

## Installation Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/bookquest.git
