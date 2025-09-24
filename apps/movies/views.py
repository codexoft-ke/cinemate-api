from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.responses import success_response, error_response
from apps.users.models import UserFavourite, Genre
from .services import TMDbService
from .serializers import FavouriteMovieSerializer, SearchQuerySerializer, PaginationQuerySerializer

User = get_user_model()


class SearchMoviesView(APIView):
    """Search movies endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        serializer = SearchQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid query parameters",
                "INVALID_PARAMS",
                serializer.errors
            )
        
        query = serializer.validated_data['q']
        page = serializer.validated_data['page']
        limit = serializer.validated_data['limit']
        
        tmdb_service = TMDbService()
        
        # Get data from TMDb
        tmdb_data = tmdb_service.search_movies(query, page)
        
        if not tmdb_data or 'results' not in tmdb_data:
            return error_response(
                "Failed to search movies",
                "SEARCH_FAILED"
            )
        
        # Format movies
        movies = [
            tmdb_service.format_movie_list_item(item, request.user)
            for item in tmdb_data['results']
        ]
        
        # Apply pagination to match our API format
        paginator = Paginator(movies, limit)
        
        try:
            page_obj = paginator.page(1)  # We already got the right page from TMDb
        except:
            page_obj = paginator.page(1)
        
        return success_response({
            "movies": movies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": tmdb_data.get('total_results', len(movies)),
                "total_pages": tmdb_data.get('total_pages', 1)
            }
        })


class PopularMoviesView(APIView):
    """Popular movies endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        serializer = PaginationQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid query parameters",
                "INVALID_PARAMS",
                serializer.errors
            )
        
        page = serializer.validated_data['page']
        limit = serializer.validated_data['limit']
        
        tmdb_service = TMDbService()
        
        # Get data from TMDb
        tmdb_data = tmdb_service.get_popular_movies(page)
        
        if not tmdb_data or 'results' not in tmdb_data:
            return error_response(
                "Failed to get popular movies",
                "FETCH_FAILED"
            )
        
        # Format movies
        movies = [
            tmdb_service.format_movie_list_item(item, request.user)
            for item in tmdb_data['results']
        ]
        
        return success_response({
            "movies": movies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": tmdb_data.get('total_results', len(movies)),
                "total_pages": tmdb_data.get('total_pages', 1)
            }
        })


class ComingSoonView(APIView):
    """Coming soon movies endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        serializer = PaginationQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid query parameters",
                "INVALID_PARAMS",
                serializer.errors
            )
        
        page = serializer.validated_data['page']
        limit = serializer.validated_data['limit']
        
        tmdb_service = TMDbService()
        
        # Get data from TMDb
        tmdb_data = tmdb_service.get_upcoming_movies(page)
        
        if not tmdb_data or 'results' not in tmdb_data:
            return error_response(
                "Failed to get upcoming movies",
                "FETCH_FAILED"
            )
        
        # Format movies
        movies = [
            tmdb_service.format_movie_list_item(item, request.user)
            for item in tmdb_data['results']
        ]
        
        return success_response({
            "movies": movies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": tmdb_data.get('total_results', len(movies)),
                "total_pages": tmdb_data.get('total_pages', 1)
            }
        })


class RecommendationsView(APIView):
    """Personalized recommendations endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = PaginationQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid query parameters",
                "INVALID_PARAMS",
                serializer.errors
            )
        
        page = serializer.validated_data['page']
        limit = serializer.validated_data['limit']
        
        tmdb_service = TMDbService()
        
        # Get personalized recommendations
        tmdb_data = tmdb_service.get_recommendations_for_user(request.user, page)
        
        if not tmdb_data or 'results' not in tmdb_data:
            return error_response(
                "Failed to get recommendations",
                "FETCH_FAILED"
            )
        
        # Format movies
        movies = [
            tmdb_service.format_movie_list_item(item, request.user)
            for item in tmdb_data['results']
        ]
        
        return success_response({
            "movies": movies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": tmdb_data.get('total_results', len(movies)),
                "total_pages": tmdb_data.get('total_pages', 1)
            }
        })


class MovieDetailsView(APIView):
    """Movie details endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request, movie_id):
        tmdb_service = TMDbService()
        
        # Get movie details from TMDb
        movie_data = tmdb_service.get_movie_details(movie_id)
        
        if not movie_data or 'success' in movie_data:
            return error_response(
                "Movie not found",
                "MOVIE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Format movie details
        movie = tmdb_service.format_movie_details(movie_data, request.user)
        
        return success_response({
            "movie": movie
        })


class FavouritesView(APIView):
    """Favourites management endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Add movie to favourites"""
        serializer = FavouriteMovieSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid data",
                "INVALID_DATA",
                serializer.errors
            )
        
        movie_id = serializer.validated_data['movie_id']
        
        # Check if already in favourites
        if UserFavourite.objects.filter(user=request.user, movie_id=movie_id).exists():
            return error_response(
                "Movie already in favourites",
                "ALREADY_FAVOURITE"
            )
        
        # Add to favourites
        UserFavourite.objects.create(user=request.user, movie_id=movie_id)
        
        return success_response(
            message="Movie added to favourites",
            status_code=status.HTTP_201_CREATED
        )
    
    def get(self, request):
        """Get user's favourite movies"""
        serializer = PaginationQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid query parameters",
                "INVALID_PARAMS",
                serializer.errors
            )
        
        page = serializer.validated_data['page']
        limit = serializer.validated_data['limit']
        
        # Get user's favourites
        favourites = UserFavourite.objects.filter(user=request.user).order_by('-created_at')
        
        # Paginate
        paginator = Paginator(favourites, limit)
        
        try:
            page_obj = paginator.page(page)
        except:
            return error_response(
                "Invalid page number",
                "INVALID_PAGE"
            )
        
        # Get movie details for favourites
        tmdb_service = TMDbService()
        movies = []
        
        for favourite in page_obj:
            movie_data = tmdb_service.get_movie_details(favourite.movie_id)
            if movie_data and 'success' not in movie_data:
                movie = tmdb_service.format_movie_list_item(movie_data, request.user)
                movies.append(movie)
        
        return success_response({
            "movies": movies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": paginator.count,
                "total_pages": paginator.num_pages
            }
        })
    
    def delete(self, request):
        """Remove movie from favourites"""
        movie_id = request.query_params.get('movie_id')
        
        if not movie_id:
            return error_response(
                "movie_id parameter is required",
                "MISSING_PARAM"
            )
        
        # Remove from favourites
        deleted_count, _ = UserFavourite.objects.filter(
            user=request.user,
            movie_id=movie_id
        ).delete()
        
        if deleted_count == 0:
            return error_response(
                "Movie not found in favourites",
                "NOT_FAVOURITE",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(message="Movie removed from favourites")


class GenresView(APIView):
    """Genres endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Sync genres from TMDb if needed
        if not Genre.objects.exists():
            tmdb_service = TMDbService()
            tmdb_service.sync_genres()
        
        # Get genres from database
        genres = Genre.objects.all().order_by('name')
        
        genres_data = [
            {
                "id": genre.id,
                "name": genre.name
            }
            for genre in genres
        ]
        
        return success_response({
            "genres": genres_data
        })