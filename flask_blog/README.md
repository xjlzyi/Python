Command:
--init
    python manage.py deploy

--migrations:
    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade


--shell:
    python manage.py shell

--run:
    python manage.py runserver --host 0.0.0.0
    python manage.py profile

--test
    python manage.py test
