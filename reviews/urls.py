from django.urls import path
from . import views

urlpatterns = [
    path('', views.listMovies, name='listMovies'),
    path('movies/<int:pk>/edit', views.edit_movie, name='edit_movie'),
    path('reviews/<int:pk>/edit', views.edit_review, name='edit_review'),
    path('filter/', views.get_filter, name='get_filter'),
    path('movies/newmovie/', views.addNewMovie, name='addNewMovie'),
    path('admin/addmovies/', views.adminAddMovie, name='adminAddMovie'),
    path('admin/reviews/movie/<int:pk>/change/', views.adminAddMovie , name='editMovie'),
    path('update/<int:pk>/', views.updateMovie, name='updateMovie'),
]
