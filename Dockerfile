FROM python:3.12

# Variables Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail
WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copier le projet
COPY . .

# Exposer le port
EXPOSE 8000