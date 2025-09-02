IM3180 Project
This is a basic Django web application (IM3180) configured to run with MySQL using Docker. The project sets up a simple web page that displays "Hello, world! Django is running with MySQL connected." and includes an admin interface. This README provides instructions to set up and run the project, along with an explanation of each file's purpose.
Prerequisites
Before running the project, ensure you have the following installed:

Docker Desktop: This is required to run the Docker containers for the Django application and MySQL database.

Installing Docker Desktop

Download Docker Desktop:

Visit the official Docker website: https://www.docker.com/products/docker-desktop/.
Select the appropriate version for your operating system (Windows, macOS, or Linux).
Download the installer.


Install Docker Desktop:

Windows:
Run the downloaded installer (Docker Desktop Installer.exe).
Follow the installation prompts. Ensure the option to enable WSL 2 (Windows Subsystem for Linux) is selected if prompted (recommended for Windows users).
Restart your computer if required.


macOS:
Open the downloaded .dmg file.
Drag the Docker Desktop application to your Applications folder.
Launch Docker Desktop from the Applications folder.


Linux:
Follow the instructions for your Linux distribution (e.g., Ubuntu, Debian) from the Docker documentation: https://docs.docker.com/desktop/install/linux-install/.
Install using the package manager or provided script.




Verify Installation:

Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux).
Run docker --version to check that Docker is installed (e.g., output: Docker version 20.10.0 or similar).
Run docker-compose --version to verify Docker Compose is installed (included with Docker Desktop).


Start Docker Desktop:

Launch Docker Desktop. It should start automatically after installation, but ensure it’s running (check the system tray on Windows/macOS for the Docker icon).
On Linux, ensure the Docker daemon is running with sudo systemctl start docker.



Project Setup and Running Instructions

Clone or Download the Project:

If using a version control system (e.g., Git), clone the repository to your local machine.
Alternatively, download and extract the project folder (IM3180) to a directory of your choice.


Navigate to the Project Directory:

Open a terminal and change to the project directory:cd /path/to/IM3180




Build and Start the Containers:

Run the following command to build the Docker images and start the services:docker-compose up --build


This command builds the Django application image and starts both the MySQL database and the web server.
Wait for the MySQL container to initialize (you’ll see logs indicating the database is ready, which may take a minute or two).


Access the Application:

Open a web browser and navigate to http://localhost:8000.
You should see the message: "Hello, world! Django is running with MySQL connected."
To access the Django admin panel, go to http://localhost:8000/admin/.


Create a Superuser for the Admin Panel (Optional):

To log in to the admin panel, you need to create a superuser. In a new terminal, run:docker-compose exec web python manage.py createsuperuser


Follow the prompts to set up a username, email, and password.
Use these credentials to log in at http://localhost:8000/admin/.


Stopping the Application:

To stop the containers, press Ctrl+C in the terminal where docker-compose up is running.
To remove the containers (preserving the database data), run:docker-compose down




Troubleshooting:

If the web page doesn’t load, ensure Docker Desktop is running and the containers started successfully (docker ps to check running containers).
If MySQL fails to connect, check the logs (docker-compose logs db) to ensure the database initialized properly.
Ensure port 8000 (web) and 3306 (MySQL) are not in use by other applications.



File Structure and Purpose
The project directory (IM3180) contains the following files:

docker-compose.yml:

Defines the services for the project: a MySQL database (db) and the Django web application (web).
Configures environment variables for the MySQL database (e.g., database name, user, password).
Maps ports (3306 for MySQL, 8000 for Django) and sets up a persistent volume for MySQL data.
Ensures the web service depends on the database and mounts the project directory into the container.


Dockerfile:

Defines the Docker image for the Django application.
Uses Python 3.12 as the base image.
Installs necessary system dependencies (e.g., default-libmysqlclient-dev for MySQL support).
Installs Python dependencies from requirements.txt and copies the project files into the container.


requirements.txt:

Lists the Python dependencies required for the project.
Includes Django==5.1 (the web framework) and mysqlclient==2.2.4 (the MySQL adapter for Django).


manage.py:

Django’s command-line utility for administrative tasks (e.g., running the server, creating migrations, or creating a superuser).
Sets the DJANGO_SETTINGS_MODULE to point to the app.settings module.


app/__init__.py:

An empty file that marks the app directory as a Python package.
Required for Python to recognize the app folder as a module.


app/asgi.py:

Configures the ASGI (Asynchronous Server Gateway Interface) for the project.
Used for asynchronous web server deployments (e.g., with tools like Uvicorn).
Sets the DJANGO_SETTINGS_MODULE to app.settings.


app/settings.py:

Contains the configuration for the Django project.
Defines settings such as the database connection (MySQL), installed apps, middleware, templates, and static file handling.
Uses environment variables to configure the MySQL database connection (e.g., database name, user, password, host, port).


app/urls.py:

Defines the URL routing for the project.
Maps the root URL ('') to a simple view that returns the "Hello, world!" message.
Includes the Django admin panel at /admin/.


app/wsgi.py:

Configures the WSGI (Web Server Gateway Interface) for the project.
Used for synchronous web server deployments (e.g., with Gunicorn).
Sets the DJANGO_SETTINGS_MODULE to app.settings.



Notes

Security: The SECRET_KEY in app/settings.py and MySQL passwords in docker-compose.yml are set for development purposes. In production, generate a secure SECRET_KEY and use stronger, unique passwords.
Database Persistence: MySQL data is stored in a Docker volume (db_data) to persist between container restarts. To reset the database, run docker-compose down -v to remove the volume.
Extending the Project: To add new Django apps, create them with docker-compose exec web python manage.py startapp <app_name> and update INSTALLED_APPS in app/settings.py.

For further assistance or to report issues, please contact the project maintainer.

SAN.CNF for regenerating SSL certs with `db` in the Subject Alternative Names (SAN) section, as shown before.

## TLDR
1) Install docker desktop and launch it
2) Open the project folder in terminal /command prompt
3) Run the following command with docker desktop opened
```
docker-compose up --build -d
```
4) Goto http://localhost:8000
5) For debugging
```
docker-compose logs
docker-compose logs web
docker-compose logs db
docker-compose exec web sh
ping 8.8.8.8
mysqladmin ping -h db -u im3180_user -psecurepassword
mysqladmin ping -h db -u im3180_user -psecurepassword --ssl-ca=/usr/local/share/ca-certificates/ca.pem
```
6) When done just enter this command
```
docker-compose down
```