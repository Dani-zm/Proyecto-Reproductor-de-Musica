from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Artista, Album, Cancion

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class StyleMixin:
    """Mixin para aplicar estilos de Bootstrap/Tema Oscuro a los campos"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Aplicar clase form-control a todos los inputs
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class ArtistaForm(StyleMixin, forms.ModelForm):
    class Meta:
        model = Artista
        fields = ['nombre', 'biografia', 'imagen']

class AlbumForm(StyleMixin, forms.ModelForm):
    class Meta:
        model = Album
        fields = ['titulo', 'artistas', 'descripcion', 'portada', 'fecha_lanzamiento', 'activo']
        widgets = {
            'fecha_lanzamiento': forms.DateInput(attrs={'type': 'date'}),
        }

class CancionForm(StyleMixin, forms.ModelForm):
    class Meta:
        model = Cancion
        fields = ['titulo', 'artistas', 'album', 'archivo', 'portada', 'minutos', 'segundos', 'activa'] 
