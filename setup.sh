python manage.py makemigrations accounts &&
python manage.py migrate accounts &&
python manage.py makemigrations &&
python manage.py makemigrations shop &&
python manage.py migrate shop &&
python manage.py migrate 

[ "$DJANGO_CREATED_SUPERUSER" = "true" ] && python manage.py createsuperuser --noinput

echo "Setup complete!"