from django.urls import path
from . import views

urlpatterns = [
    path('search', views.SearchMoviesView.as_view(), name='search-movies'),
    path('popular', views.PopularMoviesView.as_view(), name='popular-movies'),
    path('coming-soon', views.ComingSoonView.as_view(), name='coming-soon'),
    path('recommendations', views.RecommendationsView.as_view(), name='recommendations'),
    path('favourites', views.FavouritesView.as_view(), name='favourites'),
    path('genres', views.GenresView.as_view(), name='genres'),
    path('<str:movie_id>', views.MovieDetailsView.as_view(), name='movie-details'),
]