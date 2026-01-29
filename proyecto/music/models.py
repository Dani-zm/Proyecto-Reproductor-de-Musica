from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
import os

class Artista(models.Model):
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True, db_index=True)
    biografia = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='artistas/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Artista'
        verbose_name_plural = 'Artistas'
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('artista_detalle', kwargs={'slug': self.slug})
    
    @property
    def total_canciones(self):
        return self.canciones.count()
    
    @property
    def total_albums(self):
        return self.albums.count()


class Album(models.Model):
    titulo = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True, db_index=True)
    artistas = models.ManyToManyField(Artista, related_name="albums")
    descripcion = models.TextField(blank=True, null=True)
    portada = models.ImageField(upload_to='portadas_albums/', null=True, blank=True)
    fecha_lanzamiento = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_lanzamiento', 'titulo']
        verbose_name = 'Álbum'
        verbose_name_plural = 'Álbumes'
        indexes = [
            models.Index(fields=['-fecha_lanzamiento']),
        ]
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('album_detalle', kwargs={'slug': self.slug})
    
    @property
    def duracion_total(self):
        canciones = self.cancion_set.all()
        if canciones.exists():
            total_segundos = sum(c.duracion_en_segundos for c in canciones)
            minutos = total_segundos // 60
            segundos = total_segundos % 60
            return f"{minutos}:{segundos:02d}"
        return "0:00"
    
    @property
    def canciones_count(self):
        return self.cancion_set.count()
    
    def artistas_nombres(self):
        return ", ".join([artista.nombre for artista in self.artistas.all()])


class Cancion(models.Model):
    titulo = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True, db_index=True)
    artistas = models.ManyToManyField(Artista, related_name="canciones")
    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='canciones'
    )
    minutos = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(59)]
    )
    segundos = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(59)]
    )
    portada = models.ImageField(upload_to='portadas_canciones/', null=True, blank=True)
    archivo = models.FileField(upload_to='musica/', null=True, blank=True)
    reproducciones = models.PositiveIntegerField(default=0)
    favorita = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_subida', 'titulo']
        verbose_name = 'Canción'
        verbose_name_plural = 'Canciones'
        unique_together = ('titulo', 'archivo')
        indexes = [
            models.Index(fields=['-fecha_subida']),
            models.Index(fields=['favorita']),
            models.Index(fields=['activa']),
        ]
    
    def __str__(self):
        artistas = ", ".join([artista.nombre for artista in self.artistas.all()[:2]])
        if self.artistas.count() > 2:
            artistas += "..."
        return f"{self.titulo} - {artistas if artistas else 'Sin Artista'}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.titulo}-{self.pk}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('cancion_detalle', kwargs={'slug': self.slug})
    
    @property
    def duracion_en_segundos(self):
        return (self.minutos * 60) + self.segundos
    
    @property
    def duracion_formateada(self):
        return f"{self.minutos}:{self.segundos:02d}"
    
    @property
    def get_portada(self):
        """Obtiene la portada priorizando: canción > álbum > default"""
        if self.portada:
            return self.portada.url
        elif self.album and self.album.portada:
            return self.album.portada.url
        return '/static/img/default-cover.jpg'
    
    def incrementar_reproducciones(self):
        self.reproducciones += 1
        self.save(update_fields=['reproducciones'])
    
    def artistas_nombres(self):
        return ", ".join([artista.nombre for artista in self.artistas.all()])
    
    def get_nombre_archivo(self):
        if self.archivo:
            return os.path.basename(self.archivo.name)
        return ""


class Playlist(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    canciones = models.ManyToManyField(Cancion, related_name='playlists', blank=True)
    portada = models.ImageField(upload_to='playlists/', blank=True, null=True)
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='playlists',
        null=True,
        blank=True
    )
    publica = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('playlist_detalle', kwargs={'slug': self.slug})
    
    @property
    def total_canciones(self):
        return self.canciones.count()
    
    @property
    def duracion_total(self):
        canciones = self.canciones.all()
        if canciones.exists():
            total_segundos = sum(c.duracion_en_segundos for c in canciones)
            minutos = total_segundos // 60
            segundos = total_segundos % 60
            return f"{minutos}:{segundos:02d}"
        return "0:00"


class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#1DB954')  # Color en hex
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class CancionGenero(models.Model):
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='generos')
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cancion', 'genero')
        verbose_name = 'Género de Canción'
        verbose_name_plural = 'Géneros de Canciones'


class Reproduccion(models.Model):
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    fecha_reproduccion = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_reproduccion']
        verbose_name = 'Reproducción'
        verbose_name_plural = 'Reproducciones'
        indexes = [
            models.Index(fields=['-fecha_reproduccion']),
        ]
    
    def __str__(self):
        return f"{self.cancion} - {self.fecha_reproduccion}"


class Favorito(models.Model):
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='favoritos')
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='favoritos_usuarios')
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'cancion')
        ordering = ['-fecha_agregado']
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'


class ConfiguracionUsuario(models.Model):
    usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='configuracion')
    tema_oscuro = models.BooleanField(default=True)
    calidad_audio = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Baja (128kbps)'),
            ('medium', 'Media (192kbps)'),
            ('high', 'Alta (320kbps)'),
        ],
        default='high'
    )
    volumen_default = models.FloatField(default=0.7, validators=[MinValueValidator(0), MaxValueValidator(1)])
    shuffle_default = models.BooleanField(default=False)
    repeat_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Configuración de Usuario'
        verbose_name_plural = 'Configuraciones de Usuarios'
    
    def __str__(self):
        return f"Configuración de {self.usuario.username}"