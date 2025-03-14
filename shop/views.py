from django.shortcuts import render
from django.http import JsonResponse
from .forms import InstrumentFilterForm
from .models import Instrument
from django.template.loader import render_to_string

from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import ContactForm
from django.shortcuts import get_object_or_404
from .forms import InstrumentForm
from django.shortcuts import redirect
import os
import json
import time
from django.conf import settings
from django.contrib import messages


def index(request):
    return render(request, 'shop/index.html')

def productView(request,instrument_id):
    instrument = Instrument.objects.get(instrument_id=instrument_id)
    return render(request, 'shop/product.html', {'instrument': instrument})

def ShopView(request):
    form = InstrumentFilterForm(request.GET)
    queryset = Instrument.objects.select_related('category').prefetch_related('images').all()

    if form.is_valid():
      
        # Filtrare dupa model
        if form.cleaned_data.get('model'):
            queryset = queryset.filter(model__icontains=form.cleaned_data['model'])
        
        # Filtrare dupa pret
        if form.cleaned_data.get('min_price'):
            queryset = queryset.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price'):
            queryset = queryset.filter(price__lte=form.cleaned_data['max_price'])
            
        # Filtrare dupa categorie
        if form.cleaned_data.get('category'):
            queryset = queryset.filter(category__instrument=form.cleaned_data['category'])
            
        # Filtrare dupa tip
        if form.cleaned_data.get('type'):
            queryset = queryset.filter(category__type=form.cleaned_data['type'])
            
        # Filtrare dupa rating
        if form.cleaned_data.get('min_rating'):
            queryset = queryset.filter(rating__gte=form.cleaned_data['min_rating'])
            
        # Sortare
        sort = form.cleaned_data.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')
    


    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {'products': queryset}  # Creeaza contextul cu produsele filtrate
        html = render_to_string(
            template_name='shop/products_list.html',  # Template-ul pentru lista de produse
            context=context,
            request=request
        )
        return JsonResponse({'html': html})  # Returneaza HTML-ul ca raspuns JSON
    else:
        context = {
            'form': form,  
            'products': queryset, 
        }  
        return render(request, 'shop/shop.html', context) 
        

def contact(request):
    if request.method == 'GET':
        form = ContactForm()
       
    if request.method == 'POST':
       
        form = ContactForm(request.POST)
        if form.is_valid():
            # Cream directorul pentru mesaje 
            mesaje_dir = os.path.join(settings.BASE_DIR, 'shop', 'mesaje')
            os.makedirs(mesaje_dir, exist_ok=True)
            
            # Numele fisierului
            timestamp = int(time.time())
            filename = f'mesaj_{timestamp}.json'
            filepath = os.path.join(mesaje_dir, filename)
            
            # Datele pentru salvare
            mesaj_data = {
                'timestamp': timestamp,
                'nume': form.cleaned_data['nume'],
                'email': form.cleaned_data['email'],
                'subiect': form.cleaned_data['subiect'],
                'mesaj': form.cleaned_data['mesaj']
            }
        
            # Salveaza datele in fisier sub format JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mesaj_data, f, indent=4, ensure_ascii=False)
            
            messages.success(request, 'Mesajul tau a fost trimis cu succes!')
            return redirect('shop:contact')  # Redirectioneaza catre un formular gol
    else:
        form = ContactForm() 
    
    return render(request, 'shop/contact.html', {'form': form})

def add_instrument(request):
    if request.method == 'POST':
        form = InstrumentForm(request.POST)
        if form.is_valid():
            instrument = form.save()
            return redirect('shop:add_instrument') 
    else:
        form = InstrumentForm()
    
    return render(request, 'shop/add_instrument.html', {'form': form})
