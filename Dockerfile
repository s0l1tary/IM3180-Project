FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y iputils-ping \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the entire certs folder to /usr/local/share/ca-certificates/
COPY ./certs /usr/local/share/ca-certificates

# Update CA certificates
RUN update-ca-certificates

# Copy MySQL client config
COPY ./certs/my.cnf /etc/my.cnf.d/my.cnf

# Disable MariaDB SSL peer verification in dev by environment variable
ENV MARIADB_TLS_DISABLE_PEER_VERIFICATION=1

# Copy entrypoint script & make executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Start Gunicorn for production; you can replace with runserver for dev
CMD ["runserver", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
