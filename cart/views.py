from django.shortcuts import render
from accounts.models import Comanda, DetaliiComanda
from shop.models import Instrument
import json
import os
import time
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random

def cart_list(request):
    return render(request, 'cart/product_list.html')

@login_required
def process_order(request):
    if request.method == 'POST':
        try:
            # Adaugam logging pentru debugging
            cart_data = json.loads(request.body)
            print("Date primite de la client:", cart_data)  # Pentru debugging
            
            total = sum(item['price'] * item['quantity'] for item in cart_data)
            
            comanda = Comanda.objects.create(
                user=request.user,
                total=total
            )
            
            for item in cart_data:
              
                try:
                    produs = Instrument.objects.get(instrument_id=item.get('instrument_id', item.get('id')))
                    DetaliiComanda.objects.create(
                        comanda=comanda,
                        produs=produs,
                        cantitate=item['quantity'],
                        pret_unitar=item['price']
                    )
                except Instrument.DoesNotExist as e:
                    print(f"Produsul nu a fost găsit: {str(e)}")  # Pentru debugging
                    raise Exception(f"Produsul cu ID {item.get('instrument_id', item.get('id'))} nu a fost găsit")
            
            # Generam factura
            timestamp = int(time.time())
            folder_path = os.path.join(settings.MEDIA_ROOT, 'temporar-facturi', request.user.username)
            os.makedirs(folder_path, exist_ok=True)
            
            factura_path = os.path.join(folder_path, f'factura-{timestamp}.pdf')
            
            # In loc de WeasyPrint, folosim ReportLab
            doc = SimpleDocTemplate(factura_path, pagesize=letter)
            elements = []
         
            # Adaugam continutul facturii
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"Factură #{comanda.id}", styles['Title']))
            
            # Creăm tabelul cu produse
            data = [['Produs', 'Cantitate', 'Preț Unitar', 'Total']]
            for detaliu in comanda.detalii.all():
                data.append([
                    detaliu.produs.model,
                    str(detaliu.cantitate),
                    f"{detaliu.pret_unitar} lei",
                    f"{detaliu.pret_unitar * detaliu.cantitate} lei"
                ])
            
            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(t)
            doc.build(elements)
            
            # Trimitem email-ul
            email = EmailMessage(
                'Factură comandă',
                'Vă mulțumim pentru comandă! Găsiți atașată factura.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )
            
            email.attach_file(factura_path)
            email.send()
            
            return JsonResponse({'success': True, 'message': 'Comanda a fost procesată cu succes!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Metoda nepermisă'})