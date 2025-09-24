# Cinemate API Documentation
# Building a Backend for a Movie Recommendation App - ProDev BE

## Movie Recommendation Backend

### Real-World Application
This project mirrors real-world backend development scenarios where performance, security, and user-centric design are crucial.  
By completing this project, participants gain experience with:
- API development and integration.
- Implementing caching for high-performance systems.
- Documenting APIs for ease of frontend integration.

---

## Overview
This case study focuses on developing a robust backend for a movie recommendation application.  
The backend provides APIs for:
- Retrieving trending and recommended movies
- User authentication
- Saving user preferences  

It emphasizes **performance optimization** and **comprehensive API documentation**.

---

## Project Goals
The primary objectives of the movie recommendation app backend are:

- **API Creation**: Develop endpoints for fetching trending and recommended movies.  
- **User Management**: Implement user authentication and the ability to save favorite movies.  
- **Performance Optimization**: Enhance API performance with caching mechanisms.  

---

## Technologies Used
- **Django**: For backend development  
- **PostgreSQL**: Relational database for data storage  
- **Redis**: Caching system for performance optimization  
- **Swagger**: For API documentation  

---

## Key Features

### API for Movie Recommendations
- Integrate a third-party movie API (e.g., TMDb) to fetch and serve trending and recommended movie data.  
- Implement robust error handling for API calls.  

### User Authentication and Preferences
- Implement **JWT-based authentication** for secure access.  
- Create models to allow users to **save and retrieve favorite movies**.  

### Performance Optimization
- Use **Redis** for caching trending and recommended movie data.  
- Reduce API call frequency and improve response time.  

### Comprehensive Documentation
- Use **Swagger** to document all API endpoints.  
- Host Swagger documentation at **`/api/docs`** for frontend consumption.  

---

## Implementation Process

### Git Commit Workflow
**Initial Setup**
- `feat: set up Django project with PostgreSQL`
- `feat: integrate TMDb API for movie data`

**Feature Development**
- `feat: implement movie recommendation API`
- `feat: add user authentication and favorite movie storage`

**Optimization**
- `perf: add Redis caching for movie data`

**Documentation**
- `feat: integrate Swagger for API documentation`
- `docs: update README with API details`

---

## Submission Details
- **Deployment**: Host the API and Swagger documentation.  

---

## Evaluation Criteria

### Functionality
- APIs retrieve movie data accurately.  
- User authentication and favorite movie storage work seamlessly.  

### Code Quality
- Code is modular, maintainable, and well-commented.  
- Implements Python best practices and uses Django ORM effectively.  

### Performance
- Caching with Redis improves API response times.  
- Optimized database queries ensure scalability.  

### Documentation
- Swagger documentation is detailed and accessible.  
- README includes clear setup instructions.  

## Techstack
DJango
Database Postgress
Movie API themoviedb v3

## Credentials
tmdb acces token: eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhMmRjMWI1MzUzZjMyOTdmNDhlZjA0NDQ3OTE3ODBlMSIsIm5iZiI6MTc1NzQ5OTMxNC45MzIsInN1YiI6IjY4YzE0ZmIyMjlmNGNlNTAzNDRlNzFmMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.STrvrfUkHCZjAKtbGc4XskMzeyz7Hv6TZgvPS5KZ0i8

database: postgress
username: cinemate
password: Cinematedb123.
database: cinemate

## Authentication
All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## API Endpoints

### Authentication (`/auth`)

#### Login
- **POST** `/auth/login`
- **Description**: Authenticate user and generate access token
- **Request Body**:
    ```json
    {
        "email": "example@mail.com",
        "password": "PASS123"
    }
    ```
- **Response**:
    ```json
    {
        "success": true,
        "message": "Login successful",
        "data": {
            "auth_token": "<JWT_ACCESS_TOKEN>",
            "user": {
                "id": "uuid",
                "name": "Joe Doe",
                "email": "example@mail.com"
            }
        }
    }
    ```

#### Sign Up
- **POST** `/auth/signup`
- **Description**: Create new user account
- **Request Body**:
    ```json
    {
        "name": "Joe Doe",
        "email": "example@mail.com",
        "password": "PASS123",
        "genres": [1, 2, 43, 78]
    }
    ```
- **Logic**:
    - Create user account (hash password)
    - Add selected genres to user_genres table
    - Generate JWT access token
- **Response**:
    ```json
    {
        "success": true,
        "message": "Account created successfully",
        "data": {
            "auth_token": "<JWT_ACCESS_TOKEN>",
            "user": {
                "id": "uuid",
                "name": "Joe Doe",
                "email": "example@mail.com"
            }
        }
    }
    ```

#### Forgot Password
- **POST** `/auth/forgot-password`
- **Description**: Initiate password reset process
- **Request Body**:
    ```json
    {
        "email": "example@mail.com"
    }
    ```
- **Logic**:
    - Create password reset request
    - Generate 6-digit OTP code
    - Send OTP to user's email
    - Generate temporary JWT token
- **Response**:
    ```json
    {
        "success": true,
        "message": "OTP sent to your email",
        "data": {
            "reset_token": "<JWT_RESET_TOKEN>"
        }
    }
    ```

#### Verify OTP
- **POST** `/auth/forgot-password/verify`
- **Description**: Verify OTP code for password reset
- **Headers**: `Authorization: Bearer <reset_token>`
- **Request Body**:
    ```json
    {
        "otp_code": "123456"
    }
    ```
- **Logic**:
    - Verify OTP against hashed version
    - Validate IP address
    - Check request status is pending
    - Update request status to verified
- **Response**:
    ```json
    {
        "success": true,
        "message": "OTP verified successfully"
    }
    ```

#### change Password
- **POST** `/auth/forgot-password/change`
- **Description**: Reset user password
- **Headers**: `Authorization: Bearer <reset_token>`
- **Request Body**:
    ```json
    {
        "new_password": "NEWPASS123"
    }
    ```
- **Logic**:
    - Verify reset token is verified
    - Update user password (hashed)
    - Mark request as completed
    - Revoke all other pending requests
- **Response**:
    ```json
    {
        "success": true,
        "message": "Password reset successfully"
    }
    ```

#### Refresh Token
- **POST** `/auth/refresh-token`
- **Description**: Generate new access token
- **Headers**: `Authorization: Bearer <access_token>`
- **Logic**:
    - Validate current JWT token
    - Check login session status
    - Verify refresh token hasn't expired
- **Response**:
    ```json
    {
        "success": true,
        "message": "Token refreshed successfully",
        "data": {
            "auth_token": "<NEW_JWT_ACCESS_TOKEN>"
        }
    }
    ```

#### Logout
- **POST** `/auth/logout`
- **Description**: Terminate user session
- **Headers**: `Authorization: Bearer <access_token>`
- **Logic**:
    - Validate JWT token
    - Update login_session status to terminated
- **Response**:
    ```json
    {
        "success": true,
        "message": "Logged out successfully"
    }
    ```

### Movies (`/movies`)

#### Search Movies
- **GET** `/movies/search?q={query}&page={page}&limit={limit}`
- **Description**: Search movies by title, genre, or cast
- **Query Parameters**:
    - `q`: Search query (required)
    - `page`: Page number (default: 1)
    - `limit`: Items per page (default: 20, max: 50)
- **Response**: `MOVIE_LIST`

#### Popular Movies
- **GET** `/movies/popular?page={page}&limit={limit}`
- **Description**: Get popular movies
- **Response**: `MOVIE_LIST`

#### Coming Soon
- **GET** `/movies/coming-soon?page={page}&limit={limit}`
- **Description**: Get upcoming movies
- **Response**: `MOVIE_LIST`

#### Recommendations
- **GET** `/movies/recommendations`
- **Description**: Get personalized movie recommendations
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `MOVIE_LIST`

#### Movie Details
- **GET** `/movies/{id}`
- **Description**: Get detailed movie information
- **Response**: `MOVIE_DETAILS`

#### Favourites
- **POST** `/movies/favourites`
- **Description**: Add movie to favourites
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
    ```json
    {
        "movie_id": "123456"
    }
    ```

- **GET** `/movies/favourites?page={page}&limit={limit}`
- **Description**: Get user's favourite movies
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `MOVIE_LIST`

- **DELETE** `/movies/favourites?movie_id={movie_id}`
- **Description**: Remove movie from favourites
- **Headers**: `Authorization: Bearer <access_token>`

#### Genres
- **GET** `/movies/genres`
- **Description**: Get all available genres
- **Response**:
    ```json
    {
        "success": true,
        "data": {
            "genres": [
                {
                    "id": "1",
                    "name": "Action"
                }
            ]
        }
    }
    ```

### User Profile (`/profile`)

#### Get Profile
- **GET** `/profile`
- **Description**: Get user profile information
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
    ```json
    {
        "success": true,
        "data": {
            "user": {
                "id": "uuid",
                "name": "Joe Doe",
                "email": "example@mail.com",
                "genres": ["Action", "Comedy"],
                "maturity_filter": "all",
                "preferred_language": "en"
            }
        }
    }
    ```

#### Update Profile
- **POST** `/profile`
- **Description**: Update user profile
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
    ```json
    {
        "name": "Joe Doe",
        "email": "newemail@mail.com",
        "genres": [1, 2, 3],
        "maturity_filter": "teen",
        "preferred_language": "es"
    }
    ```

#### Change Password
- **POST** `/profile/change-password`
- **Description**: Change user password
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
    ```json
    {
        "old_password": "OLDPASS123",
        "new_password": "NEWPASS123"
    }
    ```
- **Logic**:
    - Validate current password
    - Update to new password (hashed)
    - Generate new access token
- **Response**:
    ```json
    {
        "success": true,
        "message": "Password changed successfully",
        "data": {
            "auth_token": "<NEW_JWT_ACCESS_TOKEN>"
        }
    }
    ```

#### Notifications
- **GET** `/profile/notifications?page={page}&limit={limit}&unread_only={boolean}`
- **Description**: Get user notifications
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
    ```json
    {
        "success": true,
        "data": {
            "notifications": "NOTIFICATION_LIST",
            "unread_count": 5,
            "pagination": {
                "page": 1,
                "limit": 20,
                "total": 100,
                "total_pages": 5
            }
        }
    }
    ```

- **POST** `/profile/notifications/read`
- **Description**: Mark notification(S) as read
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
    ```json
    {
        "notification_id": "N456" || ["N123","N456","N789"],
    }

### System (`/system`)

#### Health Check
- **GET** `/system/health`
- **Description**: API health status
- **Response**:
    ```json
    {
        "status": "healthy",
        "timestamp": "2023-01-10T15:30:20.045Z",
        "version": "1.0.0"
    }
    ```

## JWT Token Types

### Access Token
```json
{
    "user_id": "uuid",
    "session_id": "uuid",
    "type": "access_token",
    "exp": 1640995200,
    "iat": 1640908800
}
```

### Reset Token
```json
{
    "user_id": "uuid",
    "reset_id": "uuid",
    "type": "forgot_password",
    "exp": 1640995200,
    "iat": 1640908800
}
```

## Data Response Formats

### MOVIE_LIST
```json
{
    "success": true,
    "data": {
        "movies": [
            {
                "id": "19404",
                "title": "Dilwale Dulhania Le Jayenge",
                "poster": "https://image.tmdb.org/t/p/w500/2CAL2433ZeIihfX1Hb2139CX0pW.jpg",
                "backdrop": "https://image.tmdb.org/t/p/w500/90ez6ArvpO8bvpyIngBuwXOqJm5.jpg",
                "synopsis": "Raj is a rich, carefree, happy-go-lucky second generation NRI...",
                "release_date": "1995-10-20",
                "duration": 189,
                "genres": ["Comedy", "Drama", "Romance"],
                "rating": 8.7,
                "is_favorite": false,
                "is_series": false
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 1000,
            "total_pages": 50
        }
    }
}
```

### MOVIE_DETAILS
```json
{
    "success": true,
    "data": {
        "movie": {
            "id": "119051",
            "is_series": true,
            "is_favorite": false,
            "title": "Wednesday",
            "language": "English",
            "release_date": "2022-11-23",
            "rating": 8.392,
            "runtime": null, // Movie Duration if Movie
            "network_logo": "https://image.tmdb.org/t/p/w500/wwemzKWzjKYJFfCeiB57q3r4Bcm.png",
            "backdrop_url": "https://image.tmdb.org/t/p/w1280/iHSwvRVsRyxpX7FE7GbviaDvgGZ.jpg",
            "poster_url": "https://image.tmdb.org/t/p/w500/36xXlhEpQqVVPuiZhfoQuaY4OlA.jpg",
            "genres": ["Sci-Fi & Fantasy", "Mystery", "Comedy"],
            "synopsis": "Smart, sarcastic and a little dead inside...",
            "homepage": "https://www.netflix.com/title/81231974",
            "seasons": [
                {
                    "id": 182137,
                    "air_date": "2022-11-23",
                    "episode_count": 8,
                    "name": "Season 1",
                    overview: "",
                    poster_path: "https://image.tmdb.org/t/p/w500/v9fNsN3WNXObKJjBWkiKMuT3XoR.jpg",
                    season_number: 1,
                    vote_average: 8.5,
                    episodes:[
                        {
                            id: 6225573,
                            name: "Episode 1",
                            overview: "After the suspicious death of her estranged son Giorgio, ex-secret agent Sara reconnects with her former team and the life she left behind years earlier.",
                            air_date: "2025-06-03",
                            episode_number: 1,
                            runtime: 58,
                            season_number: 1,
                            still_path: "https://image.tmdb.org/t/p/w500/7fQdb4N8v9AocqlLsvwKlQNOUXr.jpg",
                            vote_average: 7
                        },
                        {
                            id: 6225573,
                            name: "Episode 1",
                            overview: "After the suspicious death of her estranged son Giorgio, ex-secret agent Sara reconnects with her former team and the life she left behind years earlier.",
                            air_date: "2025-06-03",
                            episode_number: 1,
                            runtime: 58,
                            season_number: 1,
                            still_path: "https://image.tmdb.org/t/p/w500/7fQdb4N8v9AocqlLsvwKlQNOUXr.jpg",
                            vote_average: 7
                        }
                    ]
                },
                {
                    id: 345672,
                    air_date: "2025-08-06",
                    episode_count: 8,
                    name: "Season 2",
                    overview: "",
                    poster_path: "https://image.tmdb.org/t/p/w500/aamw6JjKwTy6bdviyIcFKekSD6x.jpg",
                    season_number: 2,
                    vote_average: 7.6,
                    episodes:[
                        {
                            id: 6225573,
                            name: "Episode 1",
                            overview: "After the suspicious death of her estranged son Giorgio, ex-secret agent Sara reconnects with her former team and the life she left behind years earlier.",
                            air_date: "2025-06-03",
                            episode_number: 1,
                            runtime: 58,
                            season_number: 1,
                            still_path: "https://image.tmdb.org/t/p/w500/7fQdb4N8v9AocqlLsvwKlQNOUXr.jpg",
                            vote_average: 7
                        },
                        {
                            id: 6225573,
                            name: "Episode 1",
                            overview: "After the suspicious death of her estranged son Giorgio, ex-secret agent Sara reconnects with her former team and the life she left behind years earlier.",
                            air_date: "2025-06-03",
                            episode_number: 1,
                            runtime: 58,
                            season_number: 1,
                            still_path: "https://image.tmdb.org/t/p/w500/7fQdb4N8v9AocqlLsvwKlQNOUXr.jpg",
                            vote_average: 7
                        }
                    ]
                }
            ],
            cast: [
                {
                    id: 974169,
                    name: "Jenna Ortega",
                    profile_path: "https://image.tmdb.org/t/p/w128_and_h128_face/cV4x7jNmsGLdKZn5I6xVF3Ltnmg.jpg",
                    character: "Wednesday Addams",
                    order: 1
                },
                {
                    id: 884,
                    name: "Steve Buscemi",
                    profile_path: "https://image.tmdb.org/t/p/w128_and_h128_face/lQKdHMxfYcCBOvwRKBAxPZVNtkg.jpg",
                    character: "Barry Dort",
                    order: 3
                }
            ],
            reviews:[
                {
                    "author": "Nate Richardson",
                    "avatar": "https://image.tmdb.org/t/p/w64_and_h64_face/wBxPum8xMbwLHEFGLJcrUyGeHz8.png",
                    "rating": 9,
                    "content": "The is a sample of movie review content",
                    "created_at": "2023-01-10T15:30:20.045Z",
                    "id": "63bd848cfc31d300a8df6ea2"
                },
                {
                    "author": "Nate Richardson",
                    "avatar": "https://image.tmdb.org/t/p/w64_and_h64_face/wBxPum8xMbwLHEFGLJcrUyGeHz8.png",
                    "rating": 9,
                    "content": "The is a sample of movie review content",
                    "created_at": "2023-01-10T15:30:20.045Z",
                    "id": "63bd848cfc31d300a8df6ea2"
                }
            ],
            recommendations:[
                {
                    id: 19404,
                    title: "Dilwale Dulhania Le Jayenge",
                    poster: "https://image.tmdb.org/t/p/w500/2CAL2433ZeIihfX1Hb2139CX0pW.jpg",
                    backdrop: "https://image.tmdb.org/t/p/w500/90ez6ArvpO8bvpyIngBuwXOqJm5.jpg",
                    synopsis: "Raj is a rich, carefree, happy-go-lucky second generation NRI. Simran is the daughter of Chaudhary Baldev Singh, who in spite of being an NRI is very strict about adherence to Indian values.",
                    releaseDate: "1995-10-20",
                    duration: 189,
                    genre: ["Comedy", "Drama", "Romance"],
                    rating: 8.7,
                    isFavorite: false,
                    isSeries: false
                },
                {
                    id: 19404,
                    title: "Dilwale Dulhania Le Jayenge",
                    poster: "https://image.tmdb.org/t/p/w500/2CAL2433ZeIihfX1Hb2139CX0pW.jpg",
                    backdrop: "https://image.tmdb.org/t/p/w500/90ez6ArvpO8bvpyIngBuwXOqJm5.jpg",
                    synopsis: "Raj is a rich, carefree, happy-go-lucky second generation NRI. Simran is the daughter of Chaudhary Baldev Singh, who in spite of being an NRI is very strict about adherence to Indian values.",
                    releaseDate: "1995-10-20",
                    duration: 189,
                    genre: ["Comedy", "Drama", "Romance"],
                    rating: 8.7,
                    isFavorite: false,
                    isSeries: false
                },
            ]
        }
    }
}
```

### NOTIFICATION_LIST
```json
[
    {
        "id": "uuid",
        "title": "New Movie Added",
        "message": "A new movie 'The Dark Knight' has been added to your favorites",
        "type": "movie_added",
        "read": false,
        "created_at": "2023-01-10T15:30:20.045Z",
        "movie_id": "19404",
        "image": "https://image.tmdb.org/t/p/w500/2CAL2433ZeIihfX1Hb2139CX0pW.jpg"
    }
]
```

## Database Schema

### DATABASE SCHEMA ###
users
- id uuid (PK)
- full_name varchar(100)
- phone_number varchar(25) UNIQUE
- email_address varchar(100) UNIQUE
- hash_password varchar(255)
- is_verified boolean DEFAULT false
- last_login datetime NULL
- preferred_language varchar(10) DEFAULT 'en'
- maturity_filter enum("all","teen","adult") DEFAULT "all"
- created_at datetime
- updated_at datetime

user_favourites
- id uuid (PK)
- user_id uuid (FK -> users.id)
- movie_id varchar(50)
- created_at datetime
- updated_at datetime

user_notifications
- id uuid (PK)
- user_id uuid (FK -> users.id)
- type enum("movie_added","movie_recommendation","system_update","favorite_update") DEFAULT "movie_added"
- message text
- image text
- read boolean
- created_at datetime

user_history
- id uuid (PK)
- user_id uuid (FK -> users.id)
- movie_id varchar(50)
- created_at datetime

user_genres
- id uuid (PK)
- user_id uuid (FK -> users.id)
- genre_id varchar(50) (FK -> genres.id)
- created_at datetime
- updated_at datetime
> Unique(genre_id,user_id)

genres
- id varchar(50) (PK)
- name varchar(100)
- created_at datetime
- updated_at datetime

login_sessions
- id uuid (PK)
- user_id uuid (FK -> users.id)
- ip_address varchar(45)
- platform enum("mobile-app","web")
- device_name varchar(255)
- session_start datetime
- session_end datetime NULL
- status enum('active','terminated','expired')
- refresh_token varchar(255)
- refresh_token_expires_at datetime
- created_at datetime
- updated_at datetime

password_resets
- id uuid (PK)
- user_id uuid (FK -> users.id)
- reset_token varchar(255) UNIQUE NULLBLE
- otp_code_hash varchar(255) NULL #Hashed
- expires_at datetime
- status enum("pending","verified","completed","revoked")
- ip_address varchar(45)
- attempts int
- created_at datetime
- updated_at datetime

ip_blacklist
- id uuid (PK)
- ip_address varchar(45)
- reason text NULL
- blocked_until datetime
- created_at datetime
- updated_at datetime

## Error Response Format
```json
{
    "success": false,
    "error": {
        "code": "INVALID_CREDENTIALS",
        "message": "Invalid email or password",
        "details": {}
    }
}
```

## Rate Limiting
- Authentication endpoints: 5 requests per minute per IP
- General endpoints: 100 requests per minute per user
- Search endpoints: 30 requests per minute per user
