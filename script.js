// Handle form submission
document.getElementById("searchForm").addEventListener("submit", function(e) {
    e.preventDefault();  // Prevent the form from submitting
    const userRequest = document.getElementById("userRequest").value.toLowerCase();  // Get the user input
    displayBookSuggestions(userRequest);  // Call function to display book suggestions
});

// Display book suggestions (mock function to be replaced by API later)
function displayBookSuggestions(query) {
    const bookResultsContainer = document.getElementById("bookResults");
    bookResultsContainer.innerHTML = '';  // Clear previous results

    const mockBooks = [];  // Placeholder for actual book data

    if (mockBooks.length === 0) {
        bookResultsContainer.innerHTML = "<p>No books found matching your query.</p>";
    } else {
        mockBooks.forEach(book => {
            const bookElement = document.createElement("div");
            bookElement.classList.add("book");
            bookElement.innerHTML = `
                <img src="${book.img || 'https://via.placeholder.com/50x70'}" alt="${book.title}">
                <div>
                    <h3>${book.title}</h3>
                    <p><strong>Author:</strong> ${book.author}</p>
                    <p>${book.description}</p>
                </div>
            `;
            bookResultsContainer.appendChild(bookElement);
        });
    }
}
