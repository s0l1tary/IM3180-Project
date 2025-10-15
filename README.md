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
.\venv\Scripts\Activate.ps1

# for mac0S / Linux
source venv/bin/activate

# bypass shit
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

- install dependencies 
```
pip install -r requirements.txt

# or alternatively (since we only have 1 dependency as of now)
pip install django
```

- to run the server (ensure that you are in mysite folder)
```
python manage.py runserver
```

## other useful django commands

- To create a new app (within the 'mysite' project):
```
python manage.py startapp 
```

- To update assets such as images,etc.
    - note that each inner project subfolder (e.g. Main / Quiz / Register) should have their own static files folder. The below command collects static files from the entire project folder and places them into project root 'mysite' for reference. changes to assets should be made in the respective inner project subfolders
```
python manage.py collectstatic
```

- To create superuser
```
python manage.py createsuperuser
```

- To udpate database (whenever there are changes)
```
python manage.py makemigrations
python manage.py migrate
```

- To dump data into json file
```
python manage.py dumpdata quiz.Topic quiz.Question quiz.Option --indent 2 --output=quiz/fixtures/initial_data.json
```

- To load json file to database
```
python manage.py loaddata quiz/fixtures/initial_data.json
```

## Adding more webpages
1) Store html pages in main/templates
2) Modify main/urls.py to path to the page
3) Modify main.views.py to render the page



