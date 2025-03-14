from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.



"""
    Dupa ce creezi un user/superuser in admin
    care se creeaza doar prin introducerea unui
    username, email si parola poti sa te duci
    in pagina de admin si dupa ce dai click
    pe userul pe care doresti sa il editezi
    poti sa completezi/editezi toate campurile
    adaugandu-le in fieldsets si multe altele
"""

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'blocat')
    list_filter = ('blocat', 'is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informații Personale', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisiuni', {'fields': ('blocat', 'is_active', 'groups')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj:  # Pentru moderatori
            return ('is_staff', 'is_superuser', 'user_permissions', 'last_login', 'date_joined', 'username', 'password')
        return super().get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser and obj:  # Pentru moderatori
            return (
                (None, {'fields': ('username',)}),
                ('Informații Personale', {'fields': ('first_name', 'last_name', 'email')}),
                ('Permisiuni', {'fields': ('blocat',)}),
            )
        return super().get_fieldsets(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)