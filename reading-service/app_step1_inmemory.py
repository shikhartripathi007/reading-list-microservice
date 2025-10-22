#!/usr/bin/env python3
"""
Reading List Service - Step 1: In-Memory CRUD API
==================================================

This is the original Step 1 implementation using in-memory storage.
A simple Flask API for managing a reading list with CRUD operations.

Endpoints:
- GET /health - Health check
- GET /books - Get all books
- GET /books/<id> - Get specific book
- POST /books - Add new book
- PUT /books/<id> - Update book
- DELETE /books/<id> - Delete book

This version stores data in memory (books_storage list) and will lose
data when the server restarts. This is the baseline before database integration.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# In-memory storage for books (will be lost when server restarts)
books_storage = []
next_book_id = 1

def find_book_by_id(book_id):
    """
    Helper function to find a book by its ID in the in-memory storage.
    
    Args:
        book_id (int): The ID of the book to find
        
    Returns:
        dict or None: The book dictionary if found, None otherwise
    """
    for book in books_storage:
        if book['id'] == book_id:
            return book
    return None

def validate_book_data(data):
    """
    Validate the book data from request.
    
    Args:
        data (dict): The book data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check required fields
    if not data.get('title'):
        return False, "Title is required"
    
    if not data.get('author'):
        return False, "Author is required"
    
    # Validate status if provided
    valid_statuses = ['want-to-read', 'reading', 'completed']
    if 'status' in data and data['status'] not in valid_statuses:
        return False, f"Status must be one of: {', '.join(valid_statuses)}"
    
    # Validate rating if provided
    if 'rating' in data:
        try:
            rating = float(data['rating'])
            if rating < 1 or rating > 5:
                return False, "Rating must be between 1 and 5"
        except (ValueError, TypeError):
            return False, "Rating must be a number"
    
    return True, None

# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service is running."""
    return jsonify({
        'status': 'healthy',
        'service': 'Reading List Service',
        'timestamp': datetime.now().isoformat(),
        'total_books': len(books_storage)
    })

@app.route('/books', methods=['GET'])
def get_all_books():
    """Get all books in the reading list."""
    logger.info(f"GET /books - Returning {len(books_storage)} books")
    return jsonify({
        'books': books_storage,
        'total': len(books_storage)
    })

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """Get a specific book by ID."""
    logger.info(f"GET /books/{book_id}")
    
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book)

@app.route('/books', methods=['POST'])
def add_new_book():
    """Add a new book to the reading list."""
    global next_book_id
    
    logger.info("POST /books - Adding new book")
    
    # Parse JSON data
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Validate data
    is_valid, error_message = validate_book_data(data)
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    # Create new book
    new_book = {
        'id': next_book_id,
        'title': data['title'],
        'author': data['author'],
        'status': data.get('status', 'want-to-read'),
        'rating': data.get('rating'),
        'notes': data.get('notes', ''),
        'date_added': datetime.now().isoformat(),
        'date_updated': datetime.now().isoformat()
    }
    
    # Add to storage
    books_storage.append(new_book)
    next_book_id += 1
    
    logger.info(f"Added book: {new_book['title']} by {new_book['author']}")
    
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book."""
    logger.info(f"PUT /books/{book_id} - Updating book")
    
    # Find the book
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Parse JSON data
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Validate data (only validate fields that are being updated)
    if 'title' in data or 'author' in data:
        is_valid, error_message = validate_book_data({
            'title': data.get('title', book['title']),
            'author': data.get('author', book['author']),
            **{k: v for k, v in data.items() if k not in ['title', 'author']}
        })
        if not is_valid:
            return jsonify({'error': error_message}), 400
    
    # Update fields
    if 'title' in data:
        book['title'] = data['title']
    if 'author' in data:
        book['author'] = data['author']
    if 'status' in data:
        book['status'] = data['status']
    if 'rating' in data:
        book['rating'] = data['rating']
    if 'notes' in data:
        book['notes'] = data['notes']
    
    # Update timestamp
    book['date_updated'] = datetime.now().isoformat()
    
    logger.info(f"Updated book: {book['title']} by {book['author']}")
    
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book from the reading list."""
    logger.info(f"DELETE /books/{book_id} - Deleting book")
    
    # Find the book
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Remove from storage
    books_storage.remove(book)
    
    logger.info(f"Deleted book: {book['title']} by {book['author']}")
    
    return jsonify({
        'message': 'Book deleted successfully',
        'deleted_book': book
    })

def add_sample_data():
    """Add some sample books to get started."""
    global next_book_id
    
    sample_books = [ #do we define the schema somewhere or we can decide on the fly?
        {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'status': 'completed',
            'rating': 4.5,
            'notes': 'Excellent book on writing maintainable code'
        },
        {
            'title': 'The Pragmatic Programmer',
            'author': 'David Thomas',
            'status': 'reading',
            'rating': None,
            'notes': 'Currently reading chapter 3'
        },
        {
            'title': 'Docker Deep Dive',
            'author': 'Nigel Poulton',
            'status': 'want-to-read',
            'rating': None,
            'notes': 'Need to learn Docker for microservices'
        }
    ]
    
    for book_data in sample_books:
        book = {
            'id': next_book_id,
            'title': book_data['title'],
            'author': book_data['author'],
            'status': book_data['status'],
            'rating': book_data['rating'],
            'notes': book_data['notes'],
            'date_added': datetime.now().isoformat(),
            'date_updated': datetime.now().isoformat()
        }
        books_storage.append(book)
        next_book_id += 1
    
    logger.info(f"Added {len(sample_books)} sample books")

if __name__ == '__main__':
    # Add sample data if storage is empty
    if not books_storage:
        add_sample_data()
    
    logger.info("Starting Reading List Service...")
    logger.info("Available endpoints:")
    logger.info("  GET    /health       - Health check")
    logger.info("  GET    /books        - Get all books")
    logger.info("  GET    /books/<id>   - Get specific book")
    logger.info("  POST   /books        - Add new book")
    logger.info("  PUT    /books/<id>   - Update book")
    logger.info("  DELETE /books/<id>   - Delete book")
    
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5001, debug=True)
