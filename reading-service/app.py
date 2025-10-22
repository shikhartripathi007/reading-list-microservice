#!/usr/bin/env python3
"""
Reading List Service - A Flask API for managing your personal book collection

This service provides CRUD operations for books with the following endpoints:
- GET /books - Get all books
- GET /books/<id> - Get a specific book
- POST /books - Add a new book
- PUT /books/<id> - Update an existing book
- DELETE /books/<id> - Delete a book
- GET /health - Health check endpoint
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging

import os
import psycopg2
from psycopg2.extras import RealDictCursor #RealDictCursor: Makes database results return as dictionaries instead of tuples

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration using environment variables
DATABASE_URL = os.getenv(
    'DATABASE_URL', # what does this do?
    'postgresql://bookkeeper:mybooks123@localhost:5432/reading_list' #Connection string format: postgresql://username:password@host:port/database_name
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Database connection and helper functions
def get_db_connection():
    """Get a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor) #cursor_factory=RealDictCursor: Makes query results come back as dictionaries
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def init_database():
    """Initialize the database and create tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor() #what is cursor?
        
        # Create books table
        # is it a sql query? To understand this, following functions better.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'want-to-read',
                rating DECIMAL(2,1) CHECK (rating >= 1 AND rating <= 5),
                notes TEXT DEFAULT '',
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
        
    except psycopg2.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise

def find_book_by_id(book_id):
    """Find a book by its ID using database query"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return dict(book) if book else None
        
    except psycopg2.Error as e:
        logger.error(f"Database error in find_book_by_id: {e}")
        return None

def validate_book_data(data):
    """Validate incoming book data"""
    required_fields = ['title', 'author']
    
    if not data:
        return False, "No data provided"
    
    for field in required_fields:
        if field not in data or not data[field].strip(): #is data being treated as a map where the access is using a string key?
            return False, f"Missing required field: {field}"
    
    # Validate status if provided
    valid_statuses = ['want-to-read', 'reading', 'completed']
    if 'status' in data and data['status'] not in valid_statuses:
        return False, f"Invalid status. Must be one of: {valid_statuses}"
    
    # Validate rating if provided
    if 'rating' in data and data['rating'] is not None:
        try:
            rating = float(data['rating']) #need to understand this line, float is used to convert the rating to a float number?
            if rating < 1 or rating > 5:
                return False, "Rating must be between 1 and 5"
        except (ValueError, TypeError):
            return False, "Rating must be a number"
    
    return True, "Valid"

# ================================
# API ENDPOINTS
# ================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns the service status and basic info
    """
    try:
        # Get total books count from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books") #SQL query to count database rows
        result = cursor.fetchone() # what does this do?
        total_books = result['count'] if result else 0 # what is result['count']?
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'reading-list-api',
            'timestamp': datetime.now().isoformat(),
            'total_books': total_books
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'reading-list-api',
            'timestamp': datetime.now().isoformat(),
            'error': 'Database connection failed'
        }), 500

@app.route('/books', methods=['GET'])
def get_all_books():
    """
    Get all books in the reading list
    Returns: List of all books with their details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM books ORDER BY date_added DESC") #Books returned newest first (ORDER BY date_added DESC)
        books = cursor.fetchall() #fetchall(): Gets all rows from query result
        
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries
        books_list = [dict(book) for book in books] #why is this required?
        
        logger.info(f"GET /books - Returning {len(books_list)} books")
        
        return jsonify({
            'books': books_list,
            'total_count': len(books_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting books: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """
    Get a specific book by ID
    Args: book_id (int) - The ID of the book to retrieve
    Returns: Book details or 404 if not found
    """
    logger.info(f"GET /books/{book_id}")
    
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': f'Book with ID {book_id} not found'}), 404
    
    return jsonify({'book': book}), 200 # why not return the book directly? If wrap is required, why we didn't wrap the whole list in the above route?

@app.route('/books', methods=['POST'])
def add_new_book(): # to understand the sql queries in this function 
    """
    Add a new book to the reading list
    Expected JSON body:
    {
        "title": "Book Title",
        "author": "Author Name", 
        "status": "want-to-read|reading|completed" (optional, default: "want-to-read"),
        "rating": 1-5 (optional),
        "notes": "Personal notes" (optional)
    }
    """
    logger.info("POST /books - Adding new book")
    
    try:
        data = request.get_json() #is this like a map where the access is using a string key?
        
        # Validate the incoming data
        is_valid, message = validate_book_data(data) #is_valid gets the boolean, message gets the string
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO books (title, author, status, rating, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (
            data['title'].strip(),
            data['author'].strip(),
            data.get('status', 'want-to-read'),
            data.get('rating'),
            data.get('notes', '').strip()
        ))
        
        new_book = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        book_dict = dict(new_book) #why is this required?
        
        logger.info(f"Added book: {book_dict['title']} by {book_dict['author']}")
        
        return jsonify({
            'message': 'Book added successfully',
            'book': book_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding book: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# to understand the sql queries in this function 
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Update an existing book
    Args: book_id (int) - The ID of the book to update
    Expected JSON body: Same as POST, but all fields are optional
    """
    logger.info(f"PUT /books/{book_id} - Updating book")
    
    try:
        # Check if book exists
        book = find_book_by_id(book_id)
        if not book:
            return jsonify({'error': f'Book with ID {book_id} not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data if provided
        if 'status' in data:
            valid_statuses = ['want-to-read', 'reading', 'completed']
            if data['status'] not in valid_statuses:
                return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        if 'rating' in data and data['rating'] is not None:
            try:
                rating = float(data['rating'])
                if rating < 1 or rating > 5:
                    return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Rating must be a number'}), 400
        
        # Update in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        if 'title' in data and data['title'].strip():
            update_fields.append('title = %s')
            update_values.append(data['title'].strip())
        
        if 'author' in data and data['author'].strip():
            update_fields.append('author = %s')
            update_values.append(data['author'].strip())
        
        if 'status' in data:
            update_fields.append('status = %s')
            update_values.append(data['status'])
        
        if 'rating' in data:
            update_fields.append('rating = %s')
            update_values.append(data['rating'])
        
        if 'notes' in data:
            update_fields.append('notes = %s')
            update_values.append(data['notes'].strip())
        
        # Always update the timestamp
        update_fields.append('date_updated = CURRENT_TIMESTAMP')
        update_values.append(book_id)  # for WHERE clause
        
        if len(update_fields) > 1:  # More than just timestamp
            query = f"UPDATE books SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cursor.execute(query, update_values)
            
            updated_book = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            book_dict = dict(updated_book)
            
            logger.info(f"Updated book: {book_dict['title']} by {book_dict['author']}")
            
            return jsonify({
                'message': 'Book updated successfully',
                'book': book_dict
            }), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400
        
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book from the reading list
    Args: book_id (int) - The ID of the book to delete
    """
    logger.info(f"DELETE /books/{book_id} - Deleting book")
    
    try:
        # Check if book exists and get its details before deletion
        book = find_book_by_id(book_id)
        if not book:
            return jsonify({'error': f'Book with ID {book_id} not found'}), 404
        
        # Delete from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Deleted book: {book['title']} by {book['author']}")
        
        return jsonify({
            'message': 'Book deleted successfully',
            'deleted_book': book
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting book: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ================================
# SAMPLE DATA (for testing)
# ================================

# to understand the sql queries in this function, also the method of inserting data into the database.
def add_sample_data():
    """Add some sample books for testing to the database"""
    sample_books = [
        {
            'title': 'Flask Web Development',
            'author': 'Miguel Grinberg',
            'status': 'reading',
            'rating': None,
            'notes': 'Learning Flask for microservices'
        },
        {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'status': 'completed',
            'rating': 5,
            'notes': 'Excellent book on writing maintainable code'
        },
        {
            'title': 'Docker Deep Dive',
            'author': 'Nigel Poulton',
            'status': 'want-to-read',
            'rating': None,
            'notes': 'Next on my containerization learning path'
        }
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for book_data in sample_books:
            cursor.execute("""
                INSERT INTO books (title, author, status, rating, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                book_data['title'],
                book_data['author'],
                book_data['status'],
                book_data['rating'],
                book_data['notes']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Added {len(sample_books)} sample books to database")
        
    except psycopg2.Error as e:
        logger.error(f"Error adding sample data: {e}")
        raise

# ================================
# APPLICATION STARTUP
# ================================

if __name__ == '__main__':
    # Initialize database and create tables
    logger.info("Initializing database...")
    init_database()
    
    # Add sample data for testing (if database is empty)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        result = cursor.fetchone()
        count = result['count'] if result else 0
        cursor.close()
        conn.close()
        
        if count == 0:
            logger.info("Database is empty, adding sample data...")
            add_sample_data()
        else:
            logger.info(f"Database already has {count} books")
    except Exception as e:
        logger.error(f"Error checking database: {e}")
    
    logger.info("Starting Reading List Service...")
    logger.info("Available endpoints:")
    logger.info("  GET    /health       - Health check")
    logger.info("  GET    /books        - Get all books")
    logger.info("  GET    /books/<id>   - Get specific book")
    logger.info("  POST   /books        - Add new book")
    logger.info("  PUT    /books/<id>   - Update book")
    logger.info("  DELETE /books/<id>   - Delete book")
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',    # Listen on all network interfaces
        port=5001,         # Port 5001 (avoiding conflict with AirPlay on 5000)
        debug=True         # Enable debug mode for development
    )
