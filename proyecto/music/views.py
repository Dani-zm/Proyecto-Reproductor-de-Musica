import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models 
from django.contrib import messages
from django.db.models import Q, Count
from functools import reduce
from .models import Cancion, Artista, Album
from django.http import JsonResponse




from django.contrib.auth.decorators import login_required, user_passes_test

def es_administrador(user):
    return user.groups.filter(name='Administrador').exists() or user.is_superuser

def es_usuario(user):
    return user.groups.filter(name='Usuarios').exists()

@login_required
def redirect_based_on_role(request):
    """Vista intermedia para redirigir según el rol del usuario después del login"""
    if es_administrador(request.user):
        return redirect('admin_dashboard')
    return redirect('library')  # Cambia 'index' por 'library'

@login_required
def index(request):
    """Página principal - Si hay ID muestra reproductor, sino muestra biblioteca"""
    # Aceptar tanto 'id' como 'song_id'
    cancion_id = request.GET.get('song_id') or request.GET.get('id')
    
    print(f"DEBUG: ID recibido: {cancion_id}")
    
    # Si NO hay ID en la URL, mostrar la BIBLIOTECA
    if not cancion_id:
        print("DEBUG: No hay ID, redirigiendo a library")
        return redirect('library')
    # Si hay ID, mostrar el REPRODUCTOR con esa canción
    try:
        print(f"DEBUG: Buscando canción ID: {cancion_id}")  # <-- Agrega esto
        
        # Obtener todas las canciones activas CON archivo
        todas_canciones = Cancion.objects.filter(activa=True).exclude(
            models.Q(archivo__exact='') | models.Q(archivo__isnull=True)
        )
        lista_ids = list(todas_canciones.values_list('id', flat=True))
        
        print(f"DEBUG: Canciones con archivo disponibles: {lista_ids}")  # <-- Agrega esto
        
        # Obtener la canción solicitada
        cancion = Cancion.objects.get(id=cancion_id, activa=True)
        print(f"DEBUG: Canción encontrada: {cancion.titulo}")  # <-- Agrega esto
        
        # Verificar que tenga archivo
        if not cancion.archivo or not cancion.archivo.name:
            print(f"DEBUG: Canción no tiene archivo")  # <-- Agrega esto
            messages.warning(request, "Esta canción no tiene archivo de audio")
            if lista_ids:
                cancion = Cancion.objects.get(id=lista_ids[0])
                print(f"DEBUG: Usando canción alternativa: {cancion.id}")  # <-- Agrega esto
            else:
                # No hay canciones con archivo, redirigir a biblioteca
                messages.error(request, "No hay canciones disponibles con audio")
                print("DEBUG: No hay canciones con archivo, redirigiendo a library")  # <-- Agrega esto
                return redirect('library')
        
    except (Cancion.DoesNotExist, ValueError) as e:
        # Si la canción no existe, redirigir a biblioteca
        print(f"DEBUG: Error al buscar canción: {e}")  # <-- Agrega esto
        messages.error(request, "Canción no encontrada")
        return redirect('library')
    
    # Preparar datos para el reproductor
    artistas = Artista.objects.all()
    albums = Album.objects.all()
    
    print(f"DEBUG: Mostrando reproductor con canción: {cancion.titulo}")  # <-- Agrega esto
    return render(request, 'music/index.html', {
        'cancion': cancion,
        'artistas': artistas,
        'albums': albums,
        'lista_ids': json.dumps(lista_ids),
    })
@login_required
def library(request):
    """Vista para mostrar la biblioteca de música"""
    try:
        # Obtener artistas ordenados por nombre, con conteo de canciones
        artistas = Artista.objects.annotate(
            num_canciones=Count('canciones')
        ).order_by('nombre')[:12]
        
        # Obtener álbumes ordenados por fecha de lanzamiento
        albums = Album.objects.all().order_by('-fecha_lanzamiento')[:8]
        
        # Obtener todas las canciones para conteos
        total_canciones = Cancion.objects.count()
        
        # Datos de ejemplo para playlists
        playlists = [
            {
                'id': 1,
                'nombre': 'Canciones que te gustan',
                'descripcion': f'Lista · {total_canciones} canciones',
                'tipo_icono': 'music-note-beamed',
                'color': '#b366ff',
            },
            {
                'id': 2,
                'nombre': 'Tú episodios',
                'descripcion': 'Lista · Episodios guardados y descargados',
                'tipo_icono': 'headphones',
                'color': '#9d50bb',
            },
            {
                'id': 3,
                'nombre': 'Entrenamiento',
                'descripcion': 'Lista · Josue Reynoso',
                'tipo_icono': 'lightning-charge',
                'color': '#667eea',
            },
            {
                'id': 4,
                'nombre': 'Mi music',
                'descripcion': 'Lista · Josue Reynoso',
                'tipo_icono': 'music-player',
                'color': '#8a2be2',
            }
        ]
        
        # Datos de ejemplo para podcasts
        podcasts = [
            {
                'id': 1,
                'titulo': 'Hablando Huevadas',
                'descripcion': 'Pódcast · Sonoro | HablandoHuevadas',
                'tipo': 'podcast',
            },
            {
                'id': 2,
                'titulo': 'LA PENSION',
                'descripcion': 'Pódcast · CON FEDELOBO Y CRISS MARTELL',
                'tipo': 'podcast',
            },
            {
                'id': 3,
                'titulo': 'The Wild Project',
                'descripcion': 'Pódcast · Jordi Wild',
                'tipo': 'podcast',
            },
            {
                'id': 4,
                'titulo': 'La Cotorrisa',
                'descripcion': 'Pódcast · La Cotorrisa Podcast',
                'tipo': 'podcast',
            }
        ]
        
        # Formatear la información del artista para mostrar
        artistas_formateados = []
        for artista in artistas:
            artistas_formateados.append({
                'id': artista.id,
                'nombre': artista.nombre,
                'num_canciones': artista.num_canciones,
            })
        
        # Formatear la información del álbum
        albums_formateados = []
        for album in albums:
            # Obtener artistas del álbum
            artistas_album = album.artistas.all()
            artistas_nombres = ", ".join([artista.nombre for artista in artistas_album])
            
            albums_formateados.append({
                'id': album.id,
                'titulo': album.titulo,
                'artistas': artistas_nombres,
                'portada': album.portada,
                'fecha_lanzamiento': album.fecha_lanzamiento,
            })
        
        # Obtener canciones recientes y todas las canciones
        canciones_recientes = Cancion.objects.order_by('-id')[:12]
        todas_las_canciones = Cancion.objects.all().order_by('titulo')
        
        context = {
            'artistas': artistas_formateados,
            'albums': albums_formateados,
            'playlists': playlists,
            'podcasts': podcasts,
            'canciones_recientes': canciones_recientes,
            'todas_las_canciones': todas_las_canciones,
            'total_artistas': Artista.objects.count(),
            'total_albums': Album.objects.count(),
            'total_canciones': total_canciones,
        }
        
        return render(request, 'music/library.html', context)
        
    except Exception as e:
        print(f"Error en vista library: {e}")
        # En caso de error, mostrar página básica
        return render(request, 'music/library.html', {
            'artistas': [],
            'albums': [],
            'playlists': [],
            'podcasts': [],
            'total_artistas': 0,
            'total_albums': 0,
            'total_canciones': 0,
        })

def buscar_musica(request):
    query = request.GET.get('q', '').strip()
    current_id = request.GET.get('current_id')

    if not query:
        # Si no hay consulta, redirigir a la biblioteca
        return redirect('library')  # Ya está bien

    # Búsqueda por Título + Artista
    resultados = Cancion.objects.filter(
        Q(titulo__icontains=query) | Q(artistas__nombre__icontains=query),
        activa=True
    ).distinct()

    if resultados.exists():
        # CAMBIA ESTA LÍNEA: Redirigir al reproductor con el ID
        return redirect(f'/player/?id={resultados.first().id}')
    
    # Si no hay exacto, buscamos sugerencias por palabras sueltas
    palabras = query.split()
    sugerencias = Cancion.objects.filter(
        reduce(lambda x, y: x | y, [Q(titulo__icontains=p) | Q(artistas__nombre__icontains=p) for p in palabras]),
        activa=True
    ).distinct()

    if sugerencias.exists():
        messages.info(request, f"No encontramos '{query}', pero quizás quisiste decir: {sugerencias.first().titulo}")
        # CAMBIA ESTA LÍNEA: Redirigir al reproductor con el ID
        return redirect(f'/player/?id={sugerencias.first().id}')
    else:
        messages.error(request, f"No encontramos resultados para '{query}'.")
        # Si hay canción actual, mantenerla, sino ir a biblioteca
        if current_id:
            # CAMBIA ESTA LÍNEA: Redirigir al reproductor con el ID
            return redirect(f'/player/?id={current_id}')
        return redirect('library')

def sugerencias_busqueda(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})

    # Buscamos canciones por título o por el nombre de sus artistas
    canciones = Cancion.objects.filter(
        Q(titulo__icontains=query) | Q(artistas__nombre__icontains=query)
    ).distinct()[:5]

    results = []
    for c in canciones:
        artistas = ", ".join([a.nombre for a in c.artistas.all()])
        results.append({
            'id': c.id,
            'titulo': c.titulo,
            'artista': artistas,
            'portada': c.portada.url if c.portada else None
        })
    
    return JsonResponse({'results': results})


def cargar_mas_artistas(request):
    """API para cargar más artistas"""
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 12))
    
    artistas = Artista.objects.annotate(
        num_canciones=Count('canciones')
    ).order_by('nombre')[offset:offset + limit]
    
    data = []
    for artista in artistas:
        data.append({
            'id': artista.id,
            'nombre': artista.nombre,
            'num_canciones': artista.num_canciones,
        })
    
    return JsonResponse({
        'artistas': data,
        'has_more': Artista.objects.count() > offset + limit
    })


def cargar_mas_albums(request):
    """API para cargar más álbumes"""
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 8))
    
    albums = Album.objects.all().order_by('-fecha_lanzamiento')[offset:offset + limit]
    
    data = []
    for album in albums:
        artistas_album = album.artistas.all()
        artistas_nombres = ", ".join([artista.nombre for artista in artistas_album])
        
        data.append({
            'id': album.id,
            'titulo': album.titulo,
            'artistas': artistas_nombres,
            'portada_url': album.portada.url if album.portada else None,
            'fecha_lanzamiento': album.fecha_lanzamiento.strftime('%d/%m/%Y') if album.fecha_lanzamiento else None,
        })
    
    return JsonResponse({
        'albums': data,
        'has_more': Album.objects.count() > offset + limit
    })


def artista_detalle(request, artista_id):
    """Vista para mostrar el detalle de un artista"""
    artista = get_object_or_404(Artista, id=artista_id)
    
    # Obtener canciones del artista
    canciones = Cancion.objects.filter(artistas=artista)
    
    # Obtener álbumes del artista
    albums = Album.objects.filter(artistas=artista)
    
    context = {
        'artista': artista,
        'canciones': canciones,
        'albums': albums,
        'total_canciones': canciones.count(),
        'total_albums': albums.count(),
    }
    
    return render(request, 'music/artista_detalle.html', context)


def album_detalle(request, album_id):
    """Vista para mostrar el detalle de un álbum"""
    album = get_object_or_404(Album, id=album_id)
    
    # Obtener canciones del álbum
    canciones = Cancion.objects.filter(album=album)
    
    # Obtener artistas del álbum
    artistas = album.artistas.all()
    
    # Calcular duración total del álbum
    duracion_total_minutos = sum(c.minutos for c in canciones)
    duracion_total_segundos = sum(c.segundos for c in canciones)
    duracion_total_minutos += duracion_total_segundos // 60
    duracion_total_segundos = duracion_total_segundos % 60
    
    # Calcular valor de fondo (solo el valor para evitar errores de sintaxis en el template)
    background_value = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    if album.portada:
        background_value = f"url('{album.portada.url}')"

    context = {
        'album': album,
        'canciones': canciones,
        'artistas': artistas,
        'total_canciones': canciones.count(),
        'duracion_total': f"{duracion_total_minutos}:{str(duracion_total_segundos).zfill(2)}",
        'background_value': background_value,
    }
    
    return render(request, 'music/album_detalle.html', context)

from django.contrib.auth import login
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm, ArtistaForm, AlbumForm, CancionForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asignar grupo Usuarios por defecto
            group, created = Group.objects.get_or_create(name='Usuarios')
            user.groups.add(group)
            
            login(request, user)
            return redirect('library')  # Cambia 'index' por 'library'
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/login.html', {'form': form})


@login_required
@user_passes_test(es_administrador)
def admin_dashboard(request):
    return render(request, 'music/admin_dashboard.html', {
        'total_canciones': Cancion.objects.count(),
        'total_artistas': Artista.objects.count(),
        'total_albums': Album.objects.count(),
    })

# --- CRUD VIEWS ---

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return es_administrador(self.request.user)

# --- ARTISTA CRUD ---

class ArtistaListView(AdminRequiredMixin, ListView):
    model = Artista
    template_name = 'music/crud/lista_artistas.html'
    context_object_name = 'artistas'
    paginate_by = 20

class ArtistaCreateView(AdminRequiredMixin, CreateView):
    model = Artista
    form_class = ArtistaForm
    template_name = 'music/crud/form.html'
    success_url = reverse_lazy('lista_artistas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Artista'
        return context

class ArtistaUpdateView(AdminRequiredMixin, UpdateView):
    model = Artista
    form_class = ArtistaForm
    template_name = 'music/crud/form.html'
    success_url = reverse_lazy('lista_artistas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Artista: {self.object.nombre}'
        return context

class ArtistaDeleteView(AdminRequiredMixin, DeleteView):
    model = Artista
    template_name = 'music/crud/confirm_delete.html'
    success_url = reverse_lazy('lista_artistas')

# --- ALBUM CRUD ---

class AlbumListView(AdminRequiredMixin, ListView):
    model = Album
    template_name = 'music/crud/lista_albums.html'
    context_object_name = 'albums'
    paginate_by = 20

class AlbumCreateView(AdminRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'music/crud/form.html'
    success_url = reverse_lazy('lista_albums')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Álbum'
        return context

class AlbumUpdateView(AdminRequiredMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'music/crud/form.html'
    success_url = reverse_lazy('lista_albums')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Álbum: {self.object.titulo}'
        return context

class AlbumDeleteView(AdminRequiredMixin, DeleteView):
    model = Album
    template_name = 'music/crud/confirm_delete.html'
    success_url = reverse_lazy('lista_albums')

# --- CANCION CRUD ---

class CancionListView(AdminRequiredMixin, ListView):
    model = Cancion
    template_name = 'music/crud/lista_canciones.html'
    context_object_name = 'canciones'
    paginate_by = 20

class CancionCreateView(AdminRequiredMixin, CreateView):
    model = Cancion
    form_class = CancionForm
    template_name = 'music/crud/form.html'
    success_url = reverse_lazy('lista_canciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Canción'
        return context

class CancionUpdateView(AdminRequiredMixin, UpdateView):
    model = Cancion
    form_class = CancionForm
    template_name = 'music/crud/form.html'
    success_url = reverse_lazy('lista_canciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Canción: {self.object.titulo}'
        return context

class CancionDeleteView(AdminRequiredMixin, DeleteView):
    model = Cancion
    template_name = 'music/crud/confirm_delete.html'
    success_url = reverse_lazy('lista_canciones')
