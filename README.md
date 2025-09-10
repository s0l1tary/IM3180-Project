# Notes
- We are currently just using Django and its built in database sqlite3 and no longer using docker and mysql

## How to run?
- Prereq: have python installed with pip
- create a virtual environment
```
python -m venv [virtal environment name]
```
- activate the virtual environment
```
# for Windows users
.\venv\Scripts\activate.bat

# for mac0S / Linux
source venv/bin/activate
```

- install dependencies 
```
pip install -r requirements.txt

# or alternatively (since we only have 1 dependency as of now)
pip install django
```

- to run the server 
```
python manage.py runserver
```

## other useful django commands

- To create a new app (within the 'mysite' project):
```
python manage.py startapp 
```

- To update assets such as images,etc.
```
python manage.py migrate
python manage.py collectstatic
```

- To create superuser
```
python manage.py createsuperuser
```

- To udpate database
```
python manage.py makemigrations
python manage.py migrate
```


## Adding more webpages
1) Store html pages in main/templates
2) Modify main/urls.py to path to the page
3) Modify main.views.py to render the page



