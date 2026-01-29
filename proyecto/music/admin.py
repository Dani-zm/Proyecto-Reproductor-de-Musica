from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'total_canciones', 'total_albums', 'fecha_creacion')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artistas_nombres', 'fecha_lanzamiento', 'canciones_count')
    list_filter = ('fecha_lanzamiento', 'activo')
    search_fields = ('titulo', 'artistas__nombre')
    filter_horizontal = ('artistas',)
    prepopulated_fields = {'slug': ('titulo',)}
    readonly_fields = ('fecha_creacion', 'duracion_total')

@admin.register(Cancion)
class CancionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artistas_nombres', 'album', 'duracion_formateada', 'reproducciones', 'favorita')
    list_filter = ('favorita', 'activa', 'fecha_subida', 'album')
    search_fields = ('titulo', 'artistas__nombre', 'album__titulo')
    filter_horizontal = ('artistas',)
    prepopulated_fields = {'slug': ('titulo',)}
    readonly_fields = ('fecha_subida', 'fecha_modificacion', 'reproducciones')
    actions = ['marcar_como_favorita', 'activar_canciones']
    
    def marcar_como_favorita(self, request, queryset):
        queryset.update(favorita=True)
    marcar_como_favorita.short_description = "Marcar como favorita"
    
    def activar_canciones(self, request, queryset):
        queryset.update(activa=True)
    activar_canciones.short_description = "Activar canciones seleccionadas"

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'total_canciones', 'publica', 'fecha_creacion')
    list_filter = ('publica', 'fecha_creacion')
    search_fields = ('nombre', 'usuario__username')
    filter_horizontal = ('canciones',)
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion', 'duracion_total')

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Reproduccion)
class ReproduccionAdmin(admin.ModelAdmin):
    list_display = ('cancion', 'usuario', 'fecha_reproduccion', 'ip_address')
    list_filter = ('fecha_reproduccion',)
    search_fields = ('cancion__titulo', 'usuario__username')
    readonly_fields = ('fecha_reproduccion',)

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cancion', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('usuario__username', 'cancion__titulo')
    readonly_fields = ('fecha_agregado',)

@admin.register(ConfiguracionUsuario)
class ConfiguracionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tema_oscuro', 'calidad_audio', 'volumen_default')
    search_fields = ('usuario__username',)