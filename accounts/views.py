from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomLoginForm, CustomPasswordChangeForm
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import mail_admins
from datetime import datetime
import logging
from django.core.cache import cache
import uuid


logger = logging.getLogger('django')


def index_view(request):
    return render(request, 'accounts/index.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            logger.info(f"Incercare de inregistrare pentru email: {email}")
            
            error, message = validate_email_view(request,form)
            
            logger.info(f"Eroare pentru email: {error}  mesaj: {message}")
            if error is not None:
                print("EROARE!!!!!!!!!!!!")
                return render(request, 'exception/400.html')
            else:
                message = f"Un email de confirmare a fost trimis la adresa {email} "
                return render(request, 'accounts/status_email.html', {'message': message})
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def generate_confirmation_code():
    return str(uuid.uuid4())[:16]

def validate_email_view(request,form):
    # Form.save(commit=False) intoarce un obiect de tipul User
    # (adica formularul de tipul CustomUserCreationForm) care fost
    # completat, dar care nu e salvat in baza de date
    error = None
    try:
        user = form.save(commit=False) 
        user.cod = generate_confirmation_code()

        # Mai jos il salvam in baza de date cu tot cu codul de confirmare
        # si mai apoi trimitem email-ul de confirmare 
        user.save()
        logger.info(f"User salvat in baza de date cu codul de confirmare: {user.cod}")

        context = {
            'user': user,
            # Trimitem link-ul de confirmare in email la adresa de mail
            # link care contine codul de confirmare si care face referire
            # la functia confirma_mail 
            'confirmation_link': f"{request.scheme}://{request.get_host()}/account/confirm-email/{user.cod}/"
        }
    
        email_html = render_to_string('accounts/email_confirm.html', context)


        send_mail(
        'Confirmare cont',
        'Please confirm your email',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
            fail_silently=False,
        )


        messages.success(request, 'Te rugam sa-ti confirmi adresa de email!')
        message = f'Un email de confirmare a fost trimis la adresa {user.email}!'

    except Exception as e:
        error = str(e)
        logger.error(f"Eroare la înregistrarea utilizatorului: {str(e)}")
        html_message = f"""
        <h1 style="color: red;">Eroare la înregistrarea utilizatorului</h1>
        <p style="background-color: red; color: white; padding: 10px;">
            {str(e)}
        </p>
        """
        mail_admins(
            subject="Eroare la inregistrarea utilizatorului",
            message=f"S-a produs urmatoarea eroare: {str(e)}",
            html_message=html_message
        )
        message = f'S-a produs o eroare la trimiterea email-ului'  
    
    return (error, message)

# Pagina pe care sunt redirectionat de link-ul de confirmare din email
def confirm_mail_view(request, code):
    try:
        # Cautam in baza de date userul cu codul de confirmare
        user = CustomUser.objects.get(cod=code)
        # Ii setam email-ul confirmat
        user.email_confirmat = True
        # Salvam userul cu email-ul confirmat in baza de date
        user.save()  
        message = 'Email-ul tau a fost confirmat cu succes!'
        messages.success(request, 'Email-ul tau a fost confirmat cu succes!')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Cod de confirmare invalid!')
        message = 'S-a produs o eroare: Cod de confirmare invalid!'

    return render(request, 'accounts/status_email.html', {'message': message})


def suspicious_login_attempts_view(request, username):
    logger.critical(f"Tentative de login cu username-ul {username} de la adresa IP: {request.META.get('REMOTE_ADDR')}")
    # Daca user-ul a incercat sa se logheze de mai multe ori cu acelasi username
    # se trimite un email la admini
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'login_attempts_{ip}_{username}'
    attempts = cache.get(cache_key, [])
    current_time = datetime.now()
    
    # Adaugam incearca curenta
    attempts.append(current_time)
    # Pastram doar incercarile din ultimele 2 minute
    attempts = [t for t in attempts if (current_time - t).total_seconds() <= 120]
    cache.set(cache_key, attempts, 120)  # Expirare dupa 2 minute
                
    if len(attempts) >= 3:
        mail_admins(
            subject=f"Logari suspecte",
            html_message=f'<p>Tentative de login cu username-ul "{username}" de la adresa IP: {request.META.get("REMOTE_ADDR")}</p>'
        )

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.blocat:
                    messages.error(request, "Contul tau este blocat. Te rugam sa contactezi un administrator.")
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                return render(request, 'accounts/profile.html', {'user': user})
            else:
                messages.error(request, "Username sau parola incorecte.")
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Te-ai deconectat cu succes!')
    return redirect('index')  


def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

 
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Parola a fost schimbata cu succes!')
            return redirect('profile')
        else:
            messages.error(request, 'Te rugam sa corectezi erorile de mai jos.')
            logger.error(f"Eroare la schimbarea parolei: {form.errors}")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
