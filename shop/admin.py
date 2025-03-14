from django.contrib import admin
from .models import Instrument, Category, InstrumentImage

# LAB 4
# Creati un super user pentru site-ul vostru. X
# Din panoul admin realizati interfete pentru toate modelele ~
# Introduceti date pentru toate modelele. ~
# Schimbati ordinea afisarii campurilor pentru minim unul dintre modele ~
# Pentru fiecare model faceti un camp de cautare (search field) dupa nume, sau alta coloana relevanta. X
# Adaugati filtre laterale pentru minim un model X
# Minim un model sa aiba campurile impartite in minim 2 sectiuni X
# Personalizati pagina de administrare schimband titlurile si headerul X

admin.site.site_header = "Panou de Administrare Site"
admin.site.site_title = "Admin Site"

class InstrumentAdmin(admin.ModelAdmin):
   
    list_per_page =  10
    list_display = ['model', 'category', 'price']
    list_filter = ['category']  
    search_fields = ['model']

    # Fieldsets subdivizeaza fieldurile in grupe
    # astfel voi avea informatii de baza care vor avea model si category
    # si detalii produs care vor avea description si price
    fieldsets = [
        ('Informatii de Baza', {
            'fields': ['model', 'category']
        }),
        ('Detalii Produs', {
            'fields': ['description', 'price']
        }),
    ]
    # search_fields este un field care permite cautarea dupa un anumit field
    search_fields = ['model']

admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(Category)
admin.site.register(InstrumentImage)

