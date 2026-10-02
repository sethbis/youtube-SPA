#!/bin/bash
set -e

# Actualizar repositorios e instalar paquetes base
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv nginx git libpq-dev

# Clonar o actualizar repositorio (si se ejecuta directamente en EC2)
# cd /home/ubuntu
# git clone <URL_REPOSITORIO> Parcial-1

# Crear swap de 2GB si no existe para evitar OOM (SIGKILL 9) en t2.micro
if [ ! -f /swapfile ]; then
    echo "Configurando 2GB de memoria swap..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Configurar entorno virtual para FastAPI
cd /home/ubuntu/Parcial-1/backend
rm -rf venv
python3 -m venv venv
./venv/bin/pip install --upgrade pip setuptools wheel
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
