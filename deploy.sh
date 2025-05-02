#!/bin/bash

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip nginx

# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/NATIA-CYBER/bdi-aircraft-simple-storage-.git
cd bdi-aircraft-simple-storage-

# Install dependencies
poetry install

# Create nginx config
sudo tee /etc/nginx/sites-available/fastapi << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# Create service file
sudo tee /etc/systemd/system/fastapi.service << EOF
[Unit]
Description=FastAPI application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/bdi-aircraft-simple-storage-
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="BDI_S3_BUCKET=bdi-aircraft-simple-storage"
ExecStart=/home/ubuntu/.local/bin/poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl start fastapi
sudo systemctl enable fastapi
