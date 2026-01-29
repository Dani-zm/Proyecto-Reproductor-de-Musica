import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from music.models import Cancion, Artista, Album

def create_groups():
    # Definir grupos y sus permisos
    groups_data = {
        'Administrador': {
            'models': [Cancion, Artista, Album],
            'permissions': ['add', 'change', 'delete', 'view']
        },
        'Usuarios': {
            'models': [Cancion, Artista, Album],
            'permissions': ['view']
        }
    }

    for group_name, data in groups_data.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f'Group "{group_name}" created')
        else:
            print(f'Group "{group_name}" already exists')

        # Asignar permisos
        permissions_to_add = []
        for model in data['models']:
            content_type = ContentType.objects.get_for_model(model)
            for perm in data['permissions']:
                codename = f'{perm}_{model._meta.model_name}'
                try:
                    permission = Permission.objects.get(codename=codename, content_type=content_type)
                    permissions_to_add.append(permission)
                except Permission.DoesNotExist:
                    print(f"Permiso no encontrado: {codename}")

        group.permissions.set(permissions_to_add)
        print(f'Permisos actualizados para "{group_name}"')

if __name__ == '__main__':
    create_groups()
