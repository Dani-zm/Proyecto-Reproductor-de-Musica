from django.urls import path
from . import views

urlpatterns = [
    # Página principal - Biblioteca
    path('', views.library, name='home'),
    
    # Reproductor
    path('player/', views.index, name='player'),
    
    # Redirección después de login
    path('redirect/', views.redirect_based_on_role, name='redirect_based_on_role'),
    
    # Biblioteca (alias)
    path('library/', views.library, name='library'),
    
    # Búsqueda
    path('search/', views.buscar_musica, name='buscar'),
    path('sugerencias/', views.sugerencias_busqueda, name='sugerencias'),
    
    # APIs
    path('api/sugerencias/', views.sugerencias_busqueda, name='api_sugerencias'),
    path('api/artistas/', views.cargar_mas_artistas, name='cargar_mas_artistas'),
    path('api/albums/', views.cargar_mas_albums, name='cargar_mas_albums'),
    
    # Detalles
    path('artista/<int:artista_id>/', views.artista_detalle, name='artista_detalle'),
    path('album/<int:album_id>/', views.album_detalle, name='album_detalle'),
    
    # Autenticación
    path('signup/', views.signup, name='signup'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # CRUD Artistas
    path('artistas/', views.ArtistaListView.as_view(), name='lista_artistas'),
    path('artistas/nuevo/', views.ArtistaCreateView.as_view(), name='crear_artista'),
    path('artistas/<int:pk>/editar/', views.ArtistaUpdateView.as_view(), name='editar_artista'),
    path('artistas/<int:pk>/eliminar/', views.ArtistaDeleteView.as_view(), name='eliminar_artista'),
    
    # CRUD Álbumes
    path('albums/', views.AlbumListView.as_view(), name='lista_albums'),
    path('albums/nuevo/', views.AlbumCreateView.as_view(), name='crear_album'),
    path('albums/<int:pk>/editar/', views.AlbumUpdateView.as_view(), name='editar_album'),
    path('albums/<int:pk>/eliminar/', views.AlbumDeleteView.as_view(), name='eliminar_album'),
    
    # CRUD Canciones
    path('canciones/', views.CancionListView.as_view(), name='lista_canciones'),
    path('canciones/nuevo/', views.CancionCreateView.as_view(), name='crear_cancion'),
    path('canciones/<int:pk>/editar/', views.CancionUpdateView.as_view(), name='editar_cancion'),
    path('canciones/<int:pk>/eliminar/', views.CancionDeleteView.as_view(), name='eliminar_cancion'),
]