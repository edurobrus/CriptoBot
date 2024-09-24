from django.contrib import admin
from django.urls import path
from main import views, populate

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('cargarBD/', populate.carga, name='cargar_bd'),  # Cargar base de datos
    path('cargarWhoosh/', populate.cargaWhoosh, name='cargar_whoosh'),  # Cargar índice Whoosh
    path('peliculas/', views.list_peliculas, name='list_peliculas'),
    path('actores/', views.list_actores, name='list_actores'),
    path('detallesPelicula/<int:id>', views.detallesPelicula, name='detalles_pelicula'),
    path('detallesActor/<int:id>', views.detallesActor, name='detalles_actor'),
    path('peliculasPorActor/', views.pelicula_por_actor, name='peliculas_por_actor'),
    path('peliculasPorGenero/', views.pelicula_por_genero, name='peliculas_por_genero'),
]
