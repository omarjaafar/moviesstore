from django.urls import path
from . import views

urlpatterns = [
    path("", views.gt_map, name="gt_map"),
    path("api/movie/<int:movie_id>/locations/", views.movie_locations_api, name="movie_locations_api"),
    path("api/continents/", views.continent_popularity_api, name="continent_popularity_api"),  # ✅ new
    path("api/countries/", views.country_popularity_api, name="country_popularity_api"),
    path("api/trending/", views.trending_movies_api, name="trending_movies_api"),
]
