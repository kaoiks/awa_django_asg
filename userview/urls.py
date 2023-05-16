from django.urls import path
from . import views
urlpatterns = [
   path("", views.IndexView.as_view(), name="index"),
    path("genre/<int:pk>", views.GenreView.as_view(), name="genre"),
    path("movie/<int:pk>", views.MovieView.as_view(), name="movie"),
    path('movie/<int:pk>/rate/', views.rate_movie, name='rate_movie'),
]