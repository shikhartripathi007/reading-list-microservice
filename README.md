# 📚 Reading List Microservice

A complete CRUD microservice for managing personal reading lists, built with Flask, PostgreSQL, and Docker. This project demonstrates modern microservice architecture patterns and containerization best practices.

## 🚀 Features

- **Complete CRUD API** for managing books in your reading list
- **PostgreSQL Database** for persistent data storage
- **Docker Containerization** for easy deployment and development
- **Docker Compose** orchestration for multi-container setup
- **Health Check Endpoints** for monitoring service status
- **RESTful API Design** following industry standards

## 📖 API Endpoints

### Books Management
- `GET /books` - Retrieve all books in your reading list
- `GET /books/{id}` - Get details of a specific book
- `POST /books` - Add a new book to your list
- `PUT /books/{id}` - Update an existing book
- `DELETE /books/{id}` - Remove a book from your list

### Health Check
- `GET /health` - Check service health status

## 📋 Book Data Structure

```json
{
  "id": 1,
  "title": "The Python Cookbook",
  "author": "David Beazley", 
  "status": "reading",
  "rating": null,
  "notes": "Great for learning advanced Python"
}
```

**Status Options:** `to-read`, `reading`, `completed`  
**Rating:** 1-5 stars (optional)

## 🛠️ Prerequisites

Before running this project, ensure you have:

- **Docker** (version 20.0+)
- **Docker Compose** (version 2.0+)
- **curl** or **Postman** for API testing (optional)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd reading-list-microservice
```

### 2. Start the Application
```bash
docker-compose up --build
```

This command will:
- Build the Flask application container
- Start PostgreSQL database container
- Set up networking between containers
- Initialize the database schema

### 3. Verify the Setup
```bash
# Check if services are running
curl http://localhost:5001/health

# Expected response:
# {"status": "healthy", "database": "connected"}
```

## 📚 Usage Examples

### Add a New Book
```bash
curl -X POST http://localhost:5001/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "status": "to-read",
    "notes": "Recommended by colleagues"
  }'
```

### Get All Books
```bash
curl http://localhost:5001/books
```

### Update a Book
```bash
curl -X PUT http://localhost:5001/books/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "rating": 5,
    "notes": "Excellent book on software craftsmanship"
  }'
```

### Delete a Book
```bash
curl -X DELETE http://localhost:5001/books/1
```

## 🏗️ Project Structure

```
reading-list-microservice/
├── docker-compose.yml          # Multi-container orchestration
├── reading-service/            # Flask application
│   ├── app.py                 # Main application with PostgreSQL
│   ├── app_step1_inmemory.py  # Initial in-memory version
│   ├── Dockerfile             # Container configuration
│   └── requirements.txt       # Python dependencies
├── LEARNING_PLAN.md           # Step-by-step learning guide
└── README.md                  # This file
```

## 🔧 Development

### Running in Development Mode

For development with auto-reload:

```bash
# Start only the database
docker-compose up database

# Run Flask app locally
cd reading-service
pip install -r requirements.txt
export DATABASE_URL="postgresql://bookkeeper:mybooks123@localhost:5432/reading_list"
python app.py
```

### Database Access

Connect to PostgreSQL directly:
```bash
docker exec -it reading_list_db psql -U bookkeeper -d reading_list
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs reading-service
docker-compose logs database
```

## 🧪 Testing

### Manual Testing with curl
```bash
# Test health endpoint
curl http://localhost:5001/health

# Test CRUD operations
curl -X POST http://localhost:5001/books -H "Content-Type: application/json" -d '{"title": "Test Book", "author": "Test Author", "status": "reading"}'
curl http://localhost:5001/books
curl -X PUT http://localhost:5001/books/1 -H "Content-Type: application/json" -d '{"rating": 4}'
curl -X DELETE http://localhost:5001/books/1
```

## 🐳 Docker Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_DB`: Database name (reading_list)
- `POSTGRES_USER`: Database user (bookkeeper)
- `POSTGRES_PASSWORD`: Database password (mybooks123)

### Ports
- **Flask App**: `5001` (mapped to host)
- **PostgreSQL**: `5432` (mapped to host for development)

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :5001
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Database Connection Failed**
   ```bash
   # Check if database is healthy
   docker-compose ps
   # View database logs
   docker-compose logs database
   ```

3. **Container Build Issues**
   ```bash
   # Clean rebuild
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

## 🎓 Learning Journey

This project was built following a structured learning approach. Check out `LEARNING_PLAN.md` for:
- Step-by-step implementation guide
- Detailed explanations of each component
- Best practices and common pitfalls
- Progressive complexity from in-memory to full microservice

## 🤝 Contributing

Feel free to fork this project and submit pull requests for:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Test coverage

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Related Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Built with ❤️ for learning microservices architecture**
