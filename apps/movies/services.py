import requests
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from apps.users.models import UserFavourite, UserGenre, Genre
from typing import Dict, List, Optional

User = get_user_model()


class TMDbService:
    """Service for interacting with The Movie Database API"""
    
    def __init__(self):
        self.base_url = settings.TMDB_BASE_URL
        self.access_token = settings.TMDB_ACCESS_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make API request to TMDb"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"TMDb API error: {e}")
            return {}
    
    def search_movies(self, query: str, page: int = 1) -> dict:
        """Search for movies by title"""
        cache_key = f"tmdb_search_{query}_{page}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        params = {
            'query': query,
            'page': page,
            'include_adult': False,
            'language': 'en-US'
        }
        
        data = self._make_request('search/multi', params)
        
        # Filter only movies and TV shows
        if 'results' in data:
            data['results'] = [
                item for item in data['results'] 
                if item.get('media_type') in ['movie', 'tv']
            ]
        
        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        return data
    
    def get_popular_movies(self, page: int = 1) -> dict:
        """Get popular movies"""
        cache_key = f"tmdb_popular_{page}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        params = {
            'page': page,
            'language': 'en-US'
        }
        
        data = self._make_request('movie/popular', params)
        
        # Cache for 30 minutes
        cache.set(cache_key, data, 1800)
        return data
    
    def get_upcoming_movies(self, page: int = 1) -> dict:
        """Get upcoming movies"""
        cache_key = f"tmdb_upcoming_{page}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        params = {
            'page': page,
            'language': 'en-US'
        }
        
        data = self._make_request('movie/upcoming', params)
        
        # Cache for 1 hour
        cache.set(cache_key, data, 3600)
        return data
    
    def get_movie_details(self, movie_id: str) -> dict:
        """Get detailed movie information"""
        cache_key = f"tmdb_movie_{movie_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        params = {
            'language': 'en-US',
            'append_to_response': 'credits,reviews,recommendations,videos'
        }
        
        # Try movie first
        data = self._make_request(f'movie/{movie_id}', params)
        
        # If not found, try TV series
        if not data or 'success' in data:
            params['append_to_response'] = 'credits,reviews,recommendations,videos,seasons'
            data = self._make_request(f'tv/{movie_id}', params)
            if data and 'success' not in data:
                data['is_series'] = True
                # Get detailed season/episode info
                if 'seasons' in data:
                    for season in data['seasons']:
                        season_details = self.get_season_details(movie_id, season['season_number'])
                        season.update(season_details)
        
        # Cache for 2 hours
        cache.set(cache_key, data, 7200)
        return data
    
    def get_season_details(self, series_id: str, season_number: int) -> dict:
        """Get detailed season information"""
        cache_key = f"tmdb_season_{series_id}_{season_number}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        params = {
            'language': 'en-US'
        }
        
        data = self._make_request(f'tv/{series_id}/season/{season_number}', params)
        
        # Cache for 2 hours
        cache.set(cache_key, data, 7200)
        return data
    
    def get_genres(self) -> dict:
        """Get all available genres"""
        cache_key = "tmdb_genres"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Get both movie and TV genres
        movie_genres = self._make_request('genre/movie/list', {'language': 'en-US'})
        tv_genres = self._make_request('genre/tv/list', {'language': 'en-US'})
        
        # Combine and deduplicate
        all_genres = {}
        if 'genres' in movie_genres:
            for genre in movie_genres['genres']:
                all_genres[genre['id']] = genre
        
        if 'genres' in tv_genres:
            for genre in tv_genres['genres']:
                all_genres[genre['id']] = genre
        
        result = {'genres': list(all_genres.values())}
        
        # Cache for 24 hours
        cache.set(cache_key, result, 86400)
        return result
    
    def get_recommendations_for_user(self, user: User, page: int = 1) -> dict:
        """Get personalized recommendations based on user's favorite genres"""
        # Get user's preferred genres
        user_genres = UserGenre.objects.filter(user=user).values_list('genre_id', flat=True)
        
        if not user_genres:
            # Fallback to popular movies if no genres selected
            return self.get_popular_movies(page)
        
        cache_key = f"tmdb_recommendations_{user.id}_{page}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Use discover endpoint with user's genres
        params = {
            'with_genres': ','.join(map(str, user_genres)),
            'sort_by': 'popularity.desc',
            'page': page,
            'language': 'en-US',
            'include_adult': False
        }
        
        data = self._make_request('discover/movie', params)
        
        # Cache for 1 hour
        cache.set(cache_key, data, 3600)
        return data
    
    def format_movie_list_item(self, item: dict, user: User = None) -> dict:
        """Format movie item for API response"""
        is_series = 'first_air_date' in item or item.get('media_type') == 'tv'
        movie_id = str(item.get('id', ''))
        
        # Check if movie is in user's favorites
        is_favorite = False
        if user and user.is_authenticated:
            is_favorite = UserFavourite.objects.filter(
                user=user, 
                movie_id=movie_id
            ).exists()
        
        # Get genres
        genre_names = []
        if 'genre_ids' in item:
            # Get genre names from cache or database
            for genre_id in item['genre_ids']:
                try:
                    genre = Genre.objects.get(id=str(genre_id))
                    genre_names.append(genre.name)
                except Genre.DoesNotExist:
                    pass
        elif 'genres' in item:
            genre_names = [g['name'] for g in item['genres']]
        
        return {
            "id": movie_id,
            "title": item.get('title') or item.get('name', ''),
            "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}" if item.get('poster_path') else None,
            "backdrop": f"https://image.tmdb.org/t/p/w500{item.get('backdrop_path', '')}" if item.get('backdrop_path') else None,
            "synopsis": item.get('overview', ''),
            "release_date": item.get('release_date') or item.get('first_air_date', ''),
            "duration": item.get('runtime'),
            "genres": genre_names,
            "rating": round(item.get('vote_average', 0), 1),
            "is_favorite": is_favorite,
            "is_series": is_series
        }
    
    def format_movie_details(self, item: dict, user: User = None) -> dict:
        """Format movie details for API response"""
        is_series = item.get('is_series', False) or 'first_air_date' in item
        movie_id = str(item.get('id', ''))
        
        # Check if movie is in user's favorites
        is_favorite = False
        if user and user.is_authenticated:
            is_favorite = UserFavourite.objects.filter(
                user=user, 
                movie_id=movie_id
            ).exists()
        
        # Format cast
        cast = []
        if 'credits' in item and 'cast' in item['credits']:
            cast = [
                {
                    "id": member['id'],
                    "name": member['name'],
                    "profile_path": f"https://image.tmdb.org/t/p/w128_and_h128_face{member['profile_path']}" if member.get('profile_path') else None,
                    "character": member.get('character', ''),
                    "order": member.get('order', 999)
                }
                for member in item['credits']['cast'][:10]  # Limit to top 10
            ]
        
        # Format reviews
        reviews = []
        if 'reviews' in item and 'results' in item['reviews']:
            reviews = [
                {
                    "id": review['id'],
                    "author": review['author'],
                    "avatar": f"https://image.tmdb.org/t/p/w64_and_h64_face{review['author_details']['avatar_path']}" if review.get('author_details', {}).get('avatar_path') else None,
                    "rating": review.get('author_details', {}).get('rating'),
                    "content": review['content'][:500] + '...' if len(review['content']) > 500 else review['content'],
                    "created_at": review['created_at']
                }
                for review in item['reviews']['results'][:5]  # Limit to 5 reviews
            ]
        
        # Format recommendations
        recommendations = []
        if 'recommendations' in item and 'results' in item['recommendations']:
            recommendations = [
                self.format_movie_list_item(rec, user)
                for rec in item['recommendations']['results'][:10]  # Limit to 10
            ]
        
        # Get network logo for series
        network_logo = None
        if is_series and 'networks' in item and item['networks']:
            network = item['networks'][0]  # Take first network
            if network.get('logo_path'):
                network_logo = f"https://image.tmdb.org/t/p/w500{network['logo_path']}"
        
        # Format seasons for series
        seasons = []
        if is_series and 'seasons' in item:
            for season in item['seasons']:
                # Get episodes if available
                episodes = []
                if 'episodes' in season:
                    episodes = [
                        {
                            "id": ep['id'],
                            "name": ep['name'],
                            "overview": ep['overview'],
                            "air_date": ep.get('air_date'),
                            "episode_number": ep['episode_number'],
                            "runtime": ep.get('runtime'),
                            "season_number": ep['season_number'],
                            "still_path": f"https://image.tmdb.org/t/p/w500{ep['still_path']}" if ep.get('still_path') else None,
                            "vote_average": ep.get('vote_average', 0)
                        }
                        for ep in season['episodes']
                    ]
                
                seasons.append({
                    "id": season['id'],
                    "air_date": season.get('air_date'),
                    "episode_count": season.get('episode_count', 0),
                    "name": season['name'],
                    "overview": season.get('overview', ''),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{season['poster_path']}" if season.get('poster_path') else None,
                    "season_number": season['season_number'],
                    "vote_average": season.get('vote_average', 0),
                    "episodes": episodes
                })
        
        result = {
            "id": movie_id,
            "is_series": is_series,
            "is_favorite": is_favorite,
            "title": item.get('title') or item.get('name', ''),
            "language": 'English',  # Default, could be extracted from original_language
            "release_date": item.get('release_date') or item.get('first_air_date', ''),
            "rating": round(item.get('vote_average', 0), 1),
            "runtime": item.get('runtime'),
            "network_logo": network_logo,
            "backdrop_url": f"https://image.tmdb.org/t/p/w1280{item.get('backdrop_path', '')}" if item.get('backdrop_path') else None,
            "poster_url": f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}" if item.get('poster_path') else None,
            "genres": [g['name'] for g in item.get('genres', [])],
            "synopsis": item.get('overview', ''),
            "homepage": item.get('homepage'),
            "cast": cast,
            "reviews": reviews,
            "recommendations": recommendations
        }
        
        # Add seasons for series
        if is_series:
            result["seasons"] = seasons
        
        return result
    
    def sync_genres(self):
        """Sync genres from TMDb to local database"""
        genres_data = self.get_genres()
        
        if 'genres' in genres_data:
            for genre_data in genres_data['genres']:
                Genre.objects.update_or_create(
                    id=str(genre_data['id']),
                    defaults={
                        'name': genre_data['name']
                    }
                )