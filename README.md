# CineMate API

A robust Django REST API for a movie recommendation application with user authentication, favorites management, and TMDb integration.

## Features

- 🎬 **Movie Discovery**: Search, popular, and upcoming movies
- 👤 **User Authentication**: JWT-based auth with password reset via OTP
- ❤️ **Favorites Management**: Save and manage favorite movies
- 🎯 **Personalized Recommendations**: Based on user preferences
- 📱 **Profile Management**: User profiles with preferences
- 🔔 **Notifications**: User notification system
- 🚀 **Performance**: Redis caching for improved response times
- 📚 **API Documentation**: Swagger/OpenAPI documentation
- 🛡️ **Security**: Rate limiting and IP blacklisting

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **External API**: The Movie Database (TMDb) v3
- **Authentication**: JWT tokens
- **Documentation**: drf-spectacular (Swagger)

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- TMDb API access token

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd cinemate/api
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**:
```bash
# Create PostgreSQL database
createdb cinemate

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Sync movie genres from TMDb
python manage.py sync_genres
```

6. **Start development server**:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file with the following variables:

```env
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=cinemate
DB_USER=cinemate
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
CACHE_TTL=300

# TMDb API
TMDB_ACCESS_TOKEN=your-tmdb-access-token
TMDB_BASE_URL=https://api.themoviedb.org/3

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=604800

# Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Rate limiting
RATE_LIMIT_ENABLE=True
```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/forgot-password/verify` - Verify OTP
- `POST /auth/forgot-password/change` - Reset password
- `POST /auth/refresh-token` - Refresh access token
- `POST /auth/logout` - Logout user

### Movies

- `GET /movies/search` - Search movies
- `GET /movies/popular` - Popular movies
- `GET /movies/coming-soon` - Upcoming movies
- `GET /movies/recommendations` - Personalized recommendations (auth required)
- `GET /movies/{id}` - Movie details
- `GET /movies/favourites` - User favorites (auth required)
- `POST /movies/favourites` - Add to favorites (auth required)
- `DELETE /movies/favourites` - Remove from favorites (auth required)
- `GET /movies/genres` - Available genres

### Profile

- `GET /profile/` - Get user profile (auth required)
- `POST /profile/` - Update user profile (auth required)
- `POST /profile/change-password` - Change password (auth required)
- `GET /profile/notifications` - Get notifications (auth required)
- `POST /profile/notifications/read` - Mark notifications as read (auth required)

### System

- `GET /system/health` - Health check

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Response Format

All API responses follow a consistent format:

**Success Response**:
```json
{
    "success": true,
    "message": "Success message",
    "data": {
        // Response data
    }
}
```

**Error Response**:
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error message",
        "details": {}
    }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **Search endpoints**: 30 requests per minute per user
- **General endpoints**: 100 requests per minute per user

## Caching

The API uses Redis for caching to improve performance:

- **Movie data**: Cached for 30 minutes to 2 hours
- **Search results**: Cached for 5 minutes
- **Genres**: Cached for 24 hours

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

The project follows PEP 8 style guidelines. You can check code style with:

```bash
flake8 .
```

### Database Migrations

When making model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in production
2. Configure proper database credentials
3. Set up Redis for caching
4. Configure email backend for password reset
5. Set secure JWT secret keys
6. Configure CORS for frontend domains

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please contact the development team.# cinemate-api
