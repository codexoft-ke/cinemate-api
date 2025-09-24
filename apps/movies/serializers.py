from rest_framework import serializers


class FavouriteMovieSerializer(serializers.Serializer):
    """Serializer for adding movie to favourites"""
    movie_id = serializers.CharField(max_length=50)


class PaginationQuerySerializer(serializers.Serializer):
    """Serializer for pagination query parameters"""
    page = serializers.IntegerField(default=1, min_value=1)
    limit = serializers.IntegerField(default=20, min_value=1, max_value=50)


class SearchQuerySerializer(PaginationQuerySerializer):
    """Serializer for search query parameters"""
    q = serializers.CharField(max_length=255)