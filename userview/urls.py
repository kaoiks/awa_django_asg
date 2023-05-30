from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("movies", views.IndexView.as_view(), name="index"),
    path("search_movies", views.movie_search_view, name="movie_search"),
    path("genre/<int:pk>", views.GenreView.as_view(), name="genre"),
    path("movie/<int:pk>", views.rate_movie, name="movie"),
    path('movie/<int:pk>/rate/', views.rate_movie, name='rate_movie'),
    path("register", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path('edit_movie/<int:movie_id>/', views.edit_movie, name='edit_movie'),
]
