# Imagen base
FROM python:3.12.3

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /woopy

# Copiar archivos de requerimientos e instalar
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto 8000 (Django por defecto)
EXPOSE 8000

# Comando por defecto: aplicar migraciones y correr el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
