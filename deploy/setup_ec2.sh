#!/bin/bash
set -e

# Actualizar repositorios e instalar paquetes base
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv nginx git libpq-dev

# Clonar o actualizar repositorio (si se ejecuta directamente en EC2)
# cd /home/ubuntu
# git clone <URL_REPOSITORIO> Parcial-1

# Configurar entorno virtual para FastAPI
cd /home/ubuntu/Parcial-1/backend
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Configurar servicio systemd
sudo cp /home/ubuntu/Parcial-1/deploy/fastapi.service /etc/systemd/system/fastapi.service
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl restart fastapi

# Configurar Nginx
sudo cp /home/ubuntu/Parcial-1/deploy/nginx.conf /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl restart nginx

echo "Despliegue en EC2 completado exitosamente."
